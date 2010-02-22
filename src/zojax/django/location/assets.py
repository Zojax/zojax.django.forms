from django_assets import Bundle
from django.conf import settings
from staticfiles import settings as staticfiles_settings
import os.path


PREFIX = os.path.join(staticfiles_settings.ROOT[len(settings.MEDIA_ROOT):], "location")


locationwidget_js = Bundle(
    os.path.join(PREFIX, 'locationwidget.js'),                                    
    output="gen/locationwidget.js",                
)
