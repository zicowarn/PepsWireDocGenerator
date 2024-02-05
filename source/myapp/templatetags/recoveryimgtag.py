import os
import re
import six
from django import template
from django.template.base import Node
from django.utils.translation import gettext as _

from .. import settings

try:
    from django.utils.functional import keep_lazy
except ImportError:
    from django.core.urlresolvers import reverse
    from django.utils.functional import lazy
    keep_lazy = lambda *args, **kwargs: lazy(reverse, str)(*args, **kwargs)

register = template.Library()

@register.tag
def recoveryimgtag(parser, token):
    nodelist = parser.parse(('endrecoveryimgtag',))
    parser.delete_first_token()
    return RecoveryImgTag(nodelist)


@keep_lazy(six.text_type)
def fancy_utility_function(s, marker_infos):
    imgtag_markers = re.findall('@', s)
    for imgtag_marker in imgtag_markers:
        for marker_info in marker_infos:
            # <img src="../DELETE.jpg" alt="DELETE" width="30" height="28" border="0">
            img_attribs = ""
            marker_info_dict = eval(marker_info)
            for ky, vl in marker_info_dict.items():
                img_attribs += '%s="%s" ' % (ky, vl)
            img_attribs = img_attribs.rstrip(' ')
            img_tag = '<img %s>' % img_attribs
            s = s.replace('@', img_tag, 1)
    return s

class RecoveryImgTag(Node):
    def __init__(self, nodelist):
        self.nodelist = nodelist

    def render(self, context):
        """
        """
        template_name = context.template_name
        h2t_records_path = os.path.join(settings.BASE_DIR, 'htmlataghref.h2t')
        h2t_records = []
        with open(h2t_records_path, 'r') as h2t:
            for single_line in h2t:
                if "||" in single_line:
                    lines_infos = single_line.split('||')
                    template_name_low = template_name.lower()
                    line_info0_low = lines_infos[0].lower()
                    if template_name_low.find("\\") != -1:
                        template_name_low = template_name_low.replace("\\", "/")
                    if (template_name_low in line_info0_low or line_info0_low in template_name_low) and 'img' in lines_infos[1]:
                        img_tag_attribs = lines_infos[2]
                        h2t_records.append(img_tag_attribs)
                    else:
                        pass
                else:
                    pass
        

        return fancy_utility_function(self.nodelist.render(context).strip(), h2t_records)
