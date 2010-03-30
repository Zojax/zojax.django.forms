from django.contrib.contenttypes import generic
from django.contrib.contenttypes.models import ContentType
from django.db import models
from django.utils.translation import ugettext_lazy as _


class LocatedItem(models.Model):
    
    lat = models.FloatField(verbose_name=u"Latitude", null=False, blank=False)
    lng = models.FloatField(verbose_name=u"Longitude", null=False, blank=False)
    country = models.CharField(verbose_name=u"Country", null=True, blank=True, max_length=300)
    state = models.CharField(verbose_name=u"State", null=True, blank=True, max_length=300)
    city = models.CharField(verbose_name=u"City", null=True, blank=True, max_length=300)
    content_type = models.ForeignKey(ContentType)
    object_id = models.PositiveIntegerField()
    content_object = generic.GenericForeignKey('content_type', 'object_id')
    
    def __unicode__(self):
        return "%s:%s" % (str(self.lat), str(self.lng))
    

class BaseReference(models.Model):

    name = models.CharField(verbose_name=u"Name", null=False, blank=False, max_length=300)

    class Meta:
        abstract = True
        ordering = ['name']
        
    def __unicode__(self):
        return self.name


class Country(BaseReference):
    pass

    class Meta:
        verbose_name = _(u"Country")
        verbose_name_plural = _(u"Countries")
        ordering = ['name']


class State(BaseReference):
    country = models.ForeignKey(Country)

    class Meta:
        verbose_name = _(u"State")
        verbose_name_plural = _(u"States")
        ordering = ['name']

class City(BaseReference):
    state = models.ForeignKey(State)

    class Meta:
        verbose_name = _(u"City")
        verbose_name_plural = _(u"Cities")
        ordering = ['name']