from django.conf.urls.defaults import patterns, url, include

urlpatterns = patterns('',
    url(r'^autocomplete_countries/$', 'zojax.django.location.views.autocomplete_countries', name='location_autocomplete_countries'),
    url(r'^autocomplete_cities/$', 'zojax.django.location.views.autocomplete_cities', name='location_autocomplete_cities'),
    url(r'^autocomplete_states/$', 'zojax.django.location.views.autocomplete_states', name='location_autocomplete_states'),
)