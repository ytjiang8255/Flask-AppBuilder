import logging
from flask.ext.babelpkg import lazy_gettext
from ..base import BaseFilter, FilterRelation

log = logging.getLogger(__name__)


class FilterStartsWith(BaseFilter):
    name = lazy_gettext('Starts with')

    def apply(self, query, value):
        return query.filter(getattr(self.model, self.column_name).like(value + '%'))


class FilterNotStartsWith(BaseFilter):
    name = lazy_gettext('Not Starts with')

    def apply(self, query, value):
        return query.filter(~getattr(self.model, self.column_name).like(value + '%'))


class FilterEndsWith(BaseFilter):
    name = lazy_gettext('Ends with')

    def apply(self, query, value):
        return query.filter(getattr(self.model, self.column_name).like('%' + value))


class FilterNotEndsWith(BaseFilter):
    name = lazy_gettext('Not Ends with')

    def apply(self, query, value):
        return query.filter(~getattr(self.model, self.column_name).like('%' + value))


class FilterContains(BaseFilter):
    name = lazy_gettext('Contains')

    def apply(self, query, value):
        return query.filter(getattr(self.model, self.column_name).like('%' + value + '%'))


class FilterNotContains(BaseFilter):
    name = lazy_gettext('Not Contains')

    def apply(self, query, value):
        return query.filter(~getattr(self.model, self.column_name).like('%' + value + '%'))


class FilterEqual(BaseFilter):
    name = lazy_gettext('Equal to')

    def apply(self, query, value):
        return query.filter(getattr(self.model, self.column_name) == value)


class FilterNotEqual(BaseFilter):
    name = lazy_gettext('Not Equal to')

    def apply(self, query, value):
        return query.filter(getattr(self.model, self.column_name) != value)


class FilterGreater(BaseFilter):
    name = lazy_gettext('Greater than')

    def apply(self, query, value):
        return query.filter(getattr(self.model, self.column_name) > value)


class FilterSmaller(BaseFilter):
    name = lazy_gettext('Smaller than')

    def apply(self, query, value):
        return query.filter(getattr(self.model, self.column_name) < value)


class FilterRelationOneToManyEqual(FilterRelation):
    name = lazy_gettext('Relation')

    def apply(self, query, value):
        rel_obj = self.datamodel.get_related_obj(self.column_name, value)
        return query.filter(getattr(self.model, self.column_name) == rel_obj)


class FilterRelationOneToManyNotEqual(FilterRelation):
    name = lazy_gettext('No Relation')

    def apply(self, query, value):
        rel_obj = self.datamodel.get_related_obj(self.column_name, value)
        return query.filter(getattr(self.model, self.column_name) != rel_obj)


class FilterRelationManyToManyEqual(FilterRelation):
    name = lazy_gettext('Relation as Many')

    def apply(self, query, value):
        rel_obj = self.datamodel.get_related_obj(self.column_name, value)
        return query.filter(getattr(self.model, self.column_name).contains(rel_obj))


class FilterEqualFunction(BaseFilter):
    name = "Filter view with a function"

    def apply(self, query, func):
        return query.filter(getattr(self.model, self.column_name) == func())


class SQLAFilterConverter(object):
    """
        Class for converting columns into a supported list of filters
        specific for SQLAlchemy.

    """
    conversion_table = (('is_relation_many_to_one', [FilterRelationOneToManyEqual,
                        FilterRelationOneToManyNotEqual]),
                        ('is_relation_one_to_one', [FilterRelationOneToManyEqual,
                        FilterRelationOneToManyNotEqual]),
                        ('is_relation_many_to_many', [FilterRelationManyToManyEqual]),
                        ('is_relation_one_to_many', [FilterRelationManyToManyEqual]),
                        ('is_text', [FilterStartsWith,
                                     FilterEndsWith,
                                     FilterContains,
                                     FilterEqual,
                                     FilterNotStartsWith,
                                     FilterNotEndsWith,
                                     FilterNotContains,
                                     FilterNotEqual]),
                        ('is_string', [FilterStartsWith,
                                       FilterEndsWith,
                                       FilterContains,
                                       FilterEqual,
                                       FilterNotStartsWith,
                                       FilterNotEndsWith,
                                       FilterNotContains,
                                       FilterNotEqual]),
                        ('is_integer', [FilterEqual,
                                        FilterGreater,
                                        FilterSmaller,
                                        FilterNotEqual]),
                        ('is_float', [FilterEqual,
                                      FilterGreater,
                                      FilterSmaller,
                                      FilterNotEqual]),
                        ('is_date', [FilterEqual,
                                     FilterGreater,
                                     FilterSmaller,
                                     FilterNotEqual]),
                        ('is_datetime', [FilterEqual,
                                         FilterGreater,
                                         FilterSmaller,
                                         FilterNotEqual]),
    )

    def __init__(self, datamodel):
        self.datamodel = datamodel

    def convert(self, col_name):
        for conversion in self.conversion_table:
            if getattr(self.datamodel, conversion[0])(col_name):
                return [item(col_name, self.datamodel) for item in conversion[1]]
        log.warning('Filter type not supported for column: %s' % col_name)

