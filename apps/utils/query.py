from django.db import models
from django.db.models import Min, Max, Sum


class QuerySetDecorator:
  class Meta:
    MODEL_CLASS = models.Model

  def __init__(self, query=None):
    if query == None:
      query = self.__class__.Meta.MODEL_CLASS.objects
    self.queryset = query.all()  # Coerce RelatedManager to QuerySet

  def select_for_update(self):
    return self.__class__(self.queryset.select_for_update())

  def exclude(self, **kwargs):
    return self.__class__(self.queryset.exclude(**kwargs))

  def filter(self, **kwargs):
    return self.__class__(self.queryset.filter(**kwargs))

  def filter_field_in_range(self, field_name, lower, upper):
    kwargs = {}
    kwargs["%s__gte" % field_name] = lower
    kwargs["%s__lt" % field_name] = upper
    return self.filter(**kwargs)

  def order_by(self, *args, **kwargs):
    return self.__class__(self.queryset.order_by(*args, **kwargs))

  def get_field_sum(self, field_name):
    return self.queryset.aggregate(Sum(field_name))["%s__sum" % field_name] or 0

  def get_field_min(self, field_name):
    return self.queryset.aggregate(Min(field_name))["%s__min" % field_name]

  def get_field_max(self, field_name):
    return self.queryset.aggregate(Max(field_name))["%s__max" % field_name]

  def exists(self):
    return self.queryset.exists()

  def count(self):
    return self.queryset.count()

  def get(self, *args, **kwargs):
    return self.queryset.get(*args, **kwargs)

  def first(self):
    return self.queryset.first()

  def __iter__(self):
    return self.queryset.__iter__()

  def __bool__(self):
    return self.queryset.exists()

  def list(self):
    return list(self.queryset)

  def get_pks(self):
    return [d["pk"] for d in self.queryset.values("pk")]
