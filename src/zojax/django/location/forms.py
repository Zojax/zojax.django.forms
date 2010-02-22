from django import forms
from django.core.exceptions import ValidationError
from django.template.loader import render_to_string


class LocationWidget(forms.Widget):
    
    LAT_SUFFIX = "_lat"
    LNG_SUFFIX = "_lng"
    DEFAULT_PRECISION = "locality"
    
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
                                 'widget': self})
        
    def value_from_datadict(self, data, files, name):
        try:
            lat = float(data[name+self.LAT_SUFFIX])
            lng = float(data[name+self.LNG_SUFFIX])
            return (lat, lng)
        except:
            return None


class LocationField(forms.Field):
    
    widget = LocationWidget
    
    def clean(self, value):
        value = super(LocationField, self).clean(value)
        if not isinstance(value, tuple) or len(value) != 2 or \
            not isinstance(value[0], float) or not isinstance(value[1], float):
            raise ValidationError(u"Location must be a two floats tuple.")
        return value

