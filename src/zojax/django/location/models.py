from django.contrib.contenttypes import generic
from django.contrib.contenttypes.models import ContentType
from django.db import models
from django.utils.translation import ugettext_lazy as _


class LocatedItemManager(models.Manager):
    
    def get_for_object(self, obj):
        """
        Create a queryset matching all categories associated with the given
        object.
        """
        ctype = ContentType.objects.get_for_model(obj)
        try:
            return self.get(content_type__pk=ctype.pk,
                            object_id=obj.pk)
        except LocatedItem.DoesNotExist:
            return LocatedItem(content_object=obj)
        
    def update(self, obj, location):
        """
        Update location associated with an object.
        """
        location.content_object = obj
        location.save()


class LocatedItem(models.Model):
    
    lat = models.FloatField(verbose_name=u"Latitude", null=False, blank=False)
    lng = models.FloatField(verbose_name=u"Longitude", null=False, blank=False)
    country = models.CharField(verbose_name=u"Country", null=True, blank=True, max_length=300)
    state = models.CharField(verbose_name=u"State", null=True, blank=True, max_length=300)
    city = models.CharField(verbose_name=u"City", null=True, blank=True, max_length=300)
    content_type = models.ForeignKey(ContentType)
    object_id = models.PositiveIntegerField()
    content_object = generic.GenericForeignKey('content_type', 'object_id')
    
    objects = LocatedItemManager()
    
    def __unicode__(self):
        return "%s:%s %s, %s, %s" % (str(self.lat), str(self.lng), self.city, self.state, self.country)
    
    
class LocationField(models.ForeignKey):
    
    def __init__(self, **kw):
        super(LocationField, self).__init__(LocatedItem, **kw)
        
    
    def formfield(self, **kwargs):
        import forms
        db = kwargs.pop('using', None)
        defaults = {
            'form_class': forms.LocationField,
            'queryset': self.rel.to._default_manager.using(db).complex_filter(self.rel.limit_choices_to),
            'to_field_name': self.rel.field_name,
        }
        defaults.update(kwargs)
        return super(LocationField, self).formfield(**defaults)
    

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