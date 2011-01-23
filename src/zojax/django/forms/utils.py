import re
from django import forms
from django.core.exceptions import ValidationError
from django.utils.translation import ugettext as _

ws = re.compile('\s+')

def autostrip(cls):
    fields = [(key, value) for key, value in cls.base_fields.iteritems() if isinstance(value, forms.CharField)]
    for field_name, field_object in fields:
        def get_clean_func(original):
            return lambda value: original(value and (value.strip() or value))
        field_object.clean = get_clean_func(field_object.clean)

        def get_validate_func(original):
            def validate(value):
                original(value)
                if value and (not value.strip()):
                    raise ValidationError(_("Value shouldn't contain only whitespace characters"))
            return validate
        field_object.validate = get_validate_func(field_object.validate)
    return cls

def nowhitespace(field):
    def get_validate_func(original):
        def validate(value):
            original(value)
            if value and ws.search(value):
                raise ValidationError(_("Value shouldn't contain whitespace characters"))
        return validate
    field.validate = get_validate_func(field.validate)

__test__ = {'USAGE': """

# Few lines to configure the test environment...
>>> from django.conf import settings
>>> settings.configure()

# Lets define a form that will be used for the test. Note last line of this block, thats how
# we apply ``autostrip`` decorator.
>>> class PersonForm(forms.Form):
...     name = forms.CharField(min_length=2, max_length=10)
...     email = forms.EmailField()
...
...     def clean_name(self):
...         return self.cleaned_data['name'].capitalize()
>>> PersonForm = autostrip(PersonForm)

# Lets see how autostrip works against data with leading and trailing whitespace.
# Autostrip is performed on ``CharField``s and all its descendants such as ``EmailField``,
# ``URLField``, ``RegexField``, etc.
>>> form = PersonForm({'name': '  Victor  ', 'email': '  secret@example.ru  '})
>>> form.is_valid()
True
>>> form.cleaned_data
{'name': u'Victor', 'email': u'secret@example.ru'}

# ``clean_*`` methods works after stripping, so the letter and not the space is capitalized:
>>> form = PersonForm({'name': '  victor', 'email': 'zz@zz.zz'})
>>> form.is_valid()
True
>>> form.cleaned_data
{'name': u'Victor', 'email': u'zz@zz.zz'}

# min_length constraint is checked after strip, so it is imposible now to shut up validator with
# dummy spaces
>>> form = PersonForm({'name': '  E  ', 'email': 'zz@zz.zz'})
>>> form.is_valid()
False
>>> form.errors
{'name': [u'Ensure this value has at least 2 characters (it has 1).']}

# max_length constraint is checked after strip as well
>>> form = PersonForm({'name': '            Victor              ', 'email': 'zz@zz.zz'})
>>> form.is_valid()
True

"""}

if __name__ == "__main__":
    import doctest
    doctest.testmod()
