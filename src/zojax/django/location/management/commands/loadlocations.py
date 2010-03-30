from optparse import make_option
import os.path
import csv, zipfile, urllib, StringIO

from django.core.management.base import AppCommand
from django.core.management.base import NoArgsCommand
from django.core.management.color import no_style
from django.core.management.commands import sqlclear, syncdb
from django.core.management.commands import loaddata
from staticfiles.management.commands import build_static
from django_extensions.management.commands import syncdata
from django.db import connections, DEFAULT_DB_ALIAS
from zojax.django.location.models import City, Country, State 
from django.db import connection, transaction


_ = lambda x: x

STATE_VOCAB = {'WA': 'Washington', 'VA': 'Virginia ', 'DE': 'Delaware', 'DC': 'District of columbia', 'WI': 'Wisconsin', 'WV': 'West virginia', 'HI': 'Hawaii', 'FL': 'Florida', 'FM': 'Federated states of micronesia', 'WY': 'Wyoming', 'NH': 'New hampshire', 'NJ': 'New jersey', 'NM': 'New mexico', 'TX': 'Texas', 'LA': 'Louisiana', 'NC': 'North carolina', 'ND': 'North dakota', 'NE': 'Nebraska', 'TN': 'Tennessee', 'NY': 'New york', 'PA': 'Pennsylvania', 'CA': 'California ', 'NV': 'Nevada', 'PW': 'Palau', 'GU': 'Guam ', 'CO': 'Colorado ', 'VI': 'Virgin islands', 'AK': 'Alaska', 'AL': 'Alabama', 'AS': 'American samoa', 'AR': 'Arkansas', 'VT': 'Vermont', 'IL': 'Illinois', 'GA': 'Georgia', 'IN': 'Indiana', 'IA': 'Iowa', 'OK': 'Oklahoma', 'AZ': 'Arizona ', 'ID': 'Idaho', 'CT': 'Connecticut', 'ME': 'Maine', 'MD': 'Maryland', 'MA': 'Massachusetts', 'OH': 'Ohio', 'UT': 'Utah', 'MO': 'Missouri', 'MN': 'Minnesota', 'MI': 'Michigan', 'MH': 'Marshall islands', 'RI': 'Rhode island', 'KS': 'Kansas', 'MT': 'Montana', 'MP': 'Northern mariana islands', 'MS': 'Mississippi', 'PR': 'Puerto rico', 'SC': 'South carolina', 'KY': 'Kentucky', 'OR': 'Oregon', 'SD': 'South dakota'}

class Command(NoArgsCommand):
    help = "Load locations data."

    def handle_noargs(self, **options):
#        command = sqlclear.Command()
#        command.style = no_style()
#        res = command.handle('extendedmenus', 'treemenus')
        print "Load data..."
        zf = zipfile.ZipFile(StringIO.StringIO(urllib.urlopen('http://www.populardata.com/downloads/zip_codes.zip').read()))
        reader = csv.reader(StringIO.StringIO(zf.read('ZIP_CODES.txt')))
        countries = {'United States': {}}
        
        def prepare(name):
            return ' '.join(map(lambda x: x.lower().capitalize(), name.strip().split(' ')))
        
        for row in reader:
            if row[-1] != 'STANDARD':
                continue
            countries['United States'].setdefault(prepare(STATE_VOCAB[row[4]]), {})[prepare(row[3])] = {}

        Country.objects.all().delete()
        State.objects.all().delete()
        City.objects.all().delete()
        for country_name, states in countries.items():
            print country_name
            country = Country(name=country_name)
            country.save()
            for state_name, cities in states.items():
                state = State(name=state_name, country=country)
                state.save()
                for city_name in cities:
                    city = City(name=city_name, state=state)
                    city.save()
        print 'Done!'