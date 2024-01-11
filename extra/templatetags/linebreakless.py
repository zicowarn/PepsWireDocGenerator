import six
from django import template
from django.template.base import Node
try:
    from django.utils.functional import allow_lazy
except ImportError as se:
    from django.utils.functional import allow_lazy


register = template.Library()


@register.tag
def linebreakless(parser, token):  # @UnusedVariable
    nodelist = parser.parse(('endlinebreakless',))
    parser.delete_first_token()
    return LinebreaklessNode(nodelist)


class LinebreaklessNode(Node):
    def __init__(self, nodelist):
        self.nodelist = nodelist

    def render(self, context):
        def lazy_function(strInput):
            strInput = strInput.replace("\n\n", "\n")
            return "\n".join(filter(lambda x: not x.isspace(), strInput.split("\n")))
        strip_line_breaks = allow_lazy(lazy_function, six.text_type)
        return strip_line_breaks(self.nodelist.render(context).strip())

        
"""
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
def linebreakless(parser, token):
    nodelist = parser.parse(('endlinebreakless',))
    parser.delete_first_token()
    return LinebreaklessNode(nodelist)

class LinebreaklessNode(Node):
    def __init__(self, nodelist):
        self.nodelist = nodelist

    def render(self, context):
        strip_line_breaks = keep_lazy(six.text_type)(
            lambda x: x.replace('\n\n', '\n'))

        return strip_line_breaks(self.nodelist.render(context).strip())
"""