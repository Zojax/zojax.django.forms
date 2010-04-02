from django.contrib.contenttypes.models import ContentType
from django.db import models
from zojax.django.location.models import LocatedItem


class ModelLocationManager(models.Manager):
    """
    A manager for retrieving categories for a particular model.
    """
    def get_query_set(self):
        ctype = ContentType.objects.get_for_model(self.model)
        return LocatedItem.objects.filter(content_type__pk=ctype.pk).distinct()


class LocationDescriptor(object):
    """
    A descriptor which provides access to a ``ModelLocationManager`` for
    model classes and simple retrieval and updating of location
    for model instances.
    """
    def __get__(self, instance, owner):
        if not instance:
            manager = ModelLocationManager()
            manager.model = owner
            return manager
        else:
            return LocatedItem.objects.get_for_object(instance)

    def __set__(self, instance, value):
        LocatedItem.objects.update(instance, value)

    def __delete__(self, instance):
        LocatedItem.objects.update(instance, None)
