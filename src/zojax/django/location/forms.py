import sys

from django import forms
from django.conf import settings
from django.core.exceptions import ValidationError
from django.template.loader import render_to_string
from zojax.django.widgets.autocomplete.widgets import AutocompleteWidget
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
        lat = ''
        lng = ''
        if isinstance(value, int):
            try:
                value = LocatedItem.objects.get(id=value)
                lat = value.lat
                lng = value.lng
            except LocatedItem.DoesNotExist:
                pass
        elif isinstance(value, LocatedItem):
            lat = value.lat
            lng = value.lng
        elif value:
            lat = value[0]
            lng = value[1]
        if lat is None or lng is None:
            lat, lng = "", ""
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
        

class LocationChoiceWidget(forms.Widget):
    
    def __init__(self, attrs=None):
        self.location = LocationWidget(attrs={'showMap': False, 'readonly': False}) 
        self.city = AutocompleteWidget(choices_url='location_autocomplete_cities',
                                                                 related_fields=('state', 'country'),
                                                                 options={'autoFill': True, 'minChars': 0})
        self.state = AutocompleteWidget(choices_url='location_autocomplete_states',
                                                                 related_fields=('city', 'country'),
                                                                 options={'autoFill': True, 'minChars': 0})
        self.country = AutocompleteWidget(choices_url='location_autocomplete_countries',
                                                                 related_fields=('city', 'state'),
                                                                 options={'autoFill': True, 'minChars': 0})
        super(LocationChoiceWidget, self).__init__(attrs)

    def value_from_datadict(self, data, files, name):
        return self.location.value_from_datadict(data, files, name + '_location')
    
    def render(self, name, value, attrs=None):
        # value is a list of values, each corresponding to a widget
        # in self.widgets.
        for widget in [self.city, self.state, self.country]:
            for k, v in widget.extra.items():
                if not k.startswith(name+'_'):
                    del widget.extra[k]
                    widget.extra[name+'_' +k] = name+'_'+v
        output = []
        final_attrs = self.build_attrs(attrs)
        id_ = final_attrs.get('id', None)

        widget_value = value
        widget_name = '%s_location'%name
        widget = self.location
        if id_:
            final_attrs = dict(id='%s_location' % id_)
        output.append((widget.render(widget_name, widget_value, final_attrs), final_attrs, widget_name))

        widget_value = value.country
        widget_name = '%s_country'%name
        widget = self.country
        if id_:
            final_attrs = dict(id='%s_country' % id_)
        output.append((widget.render(widget_name, widget_value, final_attrs), final_attrs, widget_name))

        widget_value = value.state
        widget_name = '%s_state'%name
        widget = self.state
        if id_:
            final_attrs = dict(id='%s_state' % id_)
        output.append((widget.render(widget_name, widget_value, final_attrs), final_attrs, widget_name))

        widget_value = value.city
        widget_name = '%s_city'%name
        widget = self.city
        if id_:
            final_attrs = dict(id='%s_city' % id_)
        output.append((widget.render(widget_name, widget_value, final_attrs), final_attrs, widget_name))
        
        return render_to_string("location/location_choicewidget.html",
                                {'widgets': output,
                                 'widget': self})
        
    def _has_changed(self, initial, data):
        return self.location._has_changed(initial, data)

    def _get_media(self):
        "Media for a multiwidget is the combination of all media of the subwidgets"
        media = forms.widgets.Media()
        for w in [self.location, self.city, self.state, self.country]:
            media = media + w.media
        return media
    media = property(_get_media)


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
        item = LocatedItem.objects.get_for_object(form.instance)
        item.lat, item.lng, item.country, item.state, item.city = value
        if form.instance.pk is None:
            return item
        item.save()
        return item
    

class LocationChoiceField(LocationField):
    
    widget = LocationChoiceWidget