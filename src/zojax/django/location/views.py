from django.http import HttpResponse
from zojax.django.location.models import Country, City, State


def results_to_string(results):  
    if results:  
        for r in results:  
            yield '%s|%s\n' % (r.name, r.pk)  

def get_param(request, name):
    try:
        k = filter(lambda x: x.endswith(name), request.GET)[0]
    except IndexError:
        return None
    return request.REQUEST.get(k, None)


def autocomplete_countries(request):
    country = request.REQUEST.get('q', None)  
    if country:  
        res = Country.objects.filter(name__istartswith=country)  
    else:  
        res = Country.objects.all()  
    res = res[:int(request.REQUEST.get('limit', 15))]  
    return HttpResponse(results_to_string(res), content_type='text/plain')


def autocomplete_states(request):
    state = request.REQUEST.get('q', None)  
    country = get_param(request, 'country')  
    if state:  
        res = State.objects.filter(name__istartswith=state)  
    else:  
        res = State.objects.all() 
    if country:
        res = res.filter(country__name__istartswith=country)   
    res = res[:int(request.REQUEST.get('limit', 15))]  
    return HttpResponse(results_to_string(res), content_type='text/plain')


def autocomplete_cities(request):
    city = request.REQUEST.get('q', None)
    state = get_param(request, 'state')  
    if city:  
        res = City.objects.filter(name__istartswith=city)  
    else:  
        res = City.objects.all() 
    if state:
        res = res.filter(state__name__istartswith=state)   
    res = res[:int(request.REQUEST.get('limit', 15))] 
    return HttpResponse(results_to_string(res), content_type='text/plain')
