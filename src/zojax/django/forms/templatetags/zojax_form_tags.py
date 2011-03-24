import copy

from django import template
from django import forms
from django.utils.datastructures import SortedDict
from django.utils.functional import allow_lazy
from django.template.defaultfilters import stringfilter
from django.utils.encoding import force_unicode

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
            check_key = lambda key: not bool(filter(lambda x: x.startswith(key), self.fields))
        new_form.fields = SortedDict([(key, value) for key, value in form.fields.items() if check_key(key)])
        context[self.variable_name] = new_form

        return u''
    
def wrap(text, width):
    """
    A word-wrap function that preserves existing line breaks and most spaces in
    the text. Expects that existing line breaks are posix newlines.
    """
    text = force_unicode(text)
    def _generator():
        it = iter(text.split(' '))
        pos=0
        for word in it:
            if "\n" in word:
                lines = word.split('\n')
            elif len(word) > width:
                lines = [word[i:i+width] for i in xrange(len(word)/width)]
                word="\n".join(lines)
            else:
                lines = (word,)
            pos += len(lines[0]) + 1
            if pos > width:
                yield '\n'
                pos = len(lines[-1])
            else:
                yield ' '
                if len(lines) > 1:
                    pos = len(lines[-1])
            yield word
    return u''.join(_generator())
    
    
def smartwordwrap(value, arg):
    """
    Wraps words at specified line length.

    Argument: number of characters to wrap the text at.
    """
    return wrap(value, int(arg))
        
smartwordwrap.is_safe = True
smartwordwrap = stringfilter(smartwordwrap)
register.filter(smartwordwrap)
    
@register.filter
def trunc( string, number, dots='...'):
  """ 
  truncate the {string} to {number} characters
  print {dots} on the end if truncated

  usage: {{ "some text to be truncated"|trunc:6 }}
  results: some te...
  """
  if not isinstance(string, str): string = str(string)
  if len(string) <= number:
    return string
  return string[0:number]+dots