import copy

from django import template
from django import forms
from django.utils.datastructures import SortedDict

register = template.Library()

@register.tag
def get_fieldset(parser, token):
    try:
        name, fields, variable_name, form = token.split_contents()
    except ValueError:
        raise template.TemplateSyntaxError('bad arguments for %r'  % token.split_contents()[0])

    return FieldSetNode(fields.split(','), variable_name, form)

@register.tag
def get_fieldset_exclude(parser, token):
    try:
        name, fields, variable_name, form = token.split_contents()
    except ValueError:
        raise template.TemplateSyntaxError('bad arguments for %r'  % token.split_contents()[0])

    return FieldSetNode(fields.split(','), variable_name, form, True)


class FieldSetNode(template.Node):
    def __init__(self, fields, variable_name, form_variable, exclude=False):
        self.fields = fields
        self.variable_name = variable_name
        self.form_variable = form_variable
        self.exclude = exclude

    def render(self, context):
        
        form = template.Variable(self.form_variable).resolve(context)
        new_form = copy.copy(form)
        check_key = lambda key: bool(filter(lambda x: x.startswith(key), self.fields))
        if self.exclude:
            check_key = lambda key: bool(filter(lambda x: not x.startswith(key), self.fields))
            
        new_form.fields = SortedDict([(key, value) for key, value in form.fields.items() if check_key(key)])

        context[self.variable_name] = new_form

        return u''