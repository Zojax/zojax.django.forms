from django import forms
from django.core.exceptions import ValidationError
from django.template.loader import render_to_string
import simplejson


class LocationWidget(forms.Widget):
    
    LAT_SUFFIX = "_lat"
    LNG_SUFFIX = "_lng"
    COUNTRY_SUFFIX = "_country"
    CITY_SUFFIX = "_city"
    STATE_SUFFIX = "_state"
    DEFAULT_PRECISION = "postal_code"
    
    def __init__(self, *args, **kwargs):
        if 'precision' in kwargs:
            self.precision = kwargs['precision']
            del kwargs['precision']
        else:
            self.precision = self.DEFAULT_PRECISION
        super(LocationWidget, self).__init__(*args, **kwargs)
    
    def render(self, name, value, attrs=None):
        if value:
            lat = str(value[0])
            lng = str(value[1])
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
        if not isinstance(value, tuple) or len(value) != 5 or \
            not isinstance(value[0], float) or not isinstance(value[1], float):
            raise ValidationError(u"Location must be at least two floats tuple.")
        return value
    
    def widget_attrs(self, widget):
        return {'showMap': self.showMap,
                'readonly': self.readonly}
    