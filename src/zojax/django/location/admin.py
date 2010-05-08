from django.contrib import admin
from models import City, Country, State

admin.site.register([Country, State, City])
