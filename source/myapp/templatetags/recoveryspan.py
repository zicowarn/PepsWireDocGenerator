import six
from django import template
from django.template.base import Node
try:
    from django.utils.functional import keep_lazy
except ImportError:
    from django.core.urlresolvers import reverse
    from django.utils.functional import lazy
    keep_lazy = lambda *args, **kwargs: lazy(reverse, str)(*args, **kwargs)

register = template.Library()

@register.tag
def recoveryspan(parser, token):
    nodelist = parser.parse(('endrecoveryspan',))
    parser.delete_first_token()
    return RecoverySpanNode(nodelist)


@keep_lazy(six.text_type)
def fancy_utility_function(s):
    s = s.replace("[", '<span>')
    s = s.replace("]", '</span>')
    return s

class RecoverySpanNode(Node):
    def __init__(self, nodelist):
        self.nodelist = nodelist

    def render(self, context):
        return fancy_utility_function(self.nodelist.render(context).strip())
