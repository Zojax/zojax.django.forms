import sys

from django import forms
from django.conf import settings
from django.core.exceptions import ValidationError
from django.template.loader import render_to_string
import simplejson
from models import LocatedItem

class LocationWidget(forms.Widget):
    
    LAT_SUFFIX = "_lat"
    LNG_SUFFIX = "_lng"
    COUNTRY_SUFFIX = "_country"
    CITY_SUFFIX = "_city"
    STATE_SUFFIX = "_state"
    DEFAULT_PRECISION = "postal_code"
    
    class Media:
                js = ('http://maps.google.com/maps/api/js?sensor=false',
                      '%slocation/locationwidget.js' % settings.MEDIA_URL,
                )
    
    def __init__(self, *args, **kwargs):
        if 'precision' in kwargs:
            self.precision = kwargs['precision']
            del kwargs['precision']
        else:
            self.precision = self.DEFAULT_PRECISION
        super(LocationWidget, self).__init__(*args, **kwargs)
    
    def render(self, name, value, attrs=None):
        if isinstance(value, int):
            value, created = LocatedItem.objects.get_or_create(id=value)
            if value:
                lat = value.lat
                lng = value.lng
        elif value:
            lat = value[0]
            lng = value[1]
        else:
            lat = ""
            lng = ""
        return render_to_string("location/location_widget.html",
                                {'lat': lat, 'lng': lng,
                                 'name': name, 'precision': self.precision,
                                 'showMap': simplejson.dumps(self.attrs['showMap']),
                                 'readonly': simplejson.dumps(self.attrs['readonly']),
                                 'widget': self})
        
    def value_from_datadict(self, data, files, name):
        try:
            lat = float(data[name+self.LAT_SUFFIX])
            lng = float(data[name+self.LNG_SUFFIX])
            country = data[name+self.COUNTRY_SUFFIX]
            state = data[name+self.STATE_SUFFIX]
            city = data[name+self.CITY_SUFFIX]
            return (lat, lng, country, state, city)
        except:
            return None


class LocationField(forms.Field):
    
    widget = LocationWidget
    
    def __init__(self, showMap=True, readonly=False, *kv, **kw):
        self.showMap = showMap
        self.readonly = readonly
        super(LocationField, self).__init__(*kv, **kw)
        
    
    def clean(self, value):
        value = super(LocationField, self).clean(value)
        if not isinstance(value, LocatedItem):
            raise ValidationError(u"Location must be a located item object.")
        return value
    
    def widget_attrs(self, widget):
        return {'showMap': self.showMap,
                'readonly': self.readonly}
        
    def to_python(self, value):
        cur_frame = sys._getframe().f_back
        form = None
        try:
            while cur_frame is not None:
                frm = cur_frame.f_locals.get('self')
                if isinstance(frm, forms.BaseForm):
                    form = frm
                cur_frame = cur_frame.f_back
        finally:
            del cur_frame
        try:
            item = LocatedItem.objects.filter(object_id=form.instance.id)[0]
        except IndexError:
            item = LocatedItem(content_object=form.instance)
        item.lat, item.lng, item.country, item.state, item.city = value
        item.save()
        return item