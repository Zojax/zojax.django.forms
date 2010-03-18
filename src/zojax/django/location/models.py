from django.contrib.contenttypes import generic
from django.contrib.contenttypes.models import ContentType
from django.db import models


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
    
