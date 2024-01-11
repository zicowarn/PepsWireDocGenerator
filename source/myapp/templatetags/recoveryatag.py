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
def recoveryatag(parser, token):
    nodelist = parser.parse(('endrecoveryatag',))
    parser.delete_first_token()
    return RecoveryATag(nodelist)


@keep_lazy(six.text_type)
def fancy_utility_function(s, marker_infos):
    atag_markers = re.findall('''#[\[\w_a-zA-Z0-9_+&.、：;":'。,，=\)\(/）（\-\s\]]*#{1}''', re.sub('#[a-f0-9]{4}', "", s))
    for atag_marker in atag_markers:
        if re.match('#[a-f0-9]{4}', atag_marker):
            continue # filter color value likes #FFFFFF
        atag_marker_tocheck = atag_marker
        atag_marker_tocheck = atag_marker_tocheck.lstrip('#')
        atag_marker_tocheck = atag_marker_tocheck.rstrip('#')
        atag_marker_tocheck = atag_marker_tocheck.lstrip('[')
        atag_marker_tocheck = atag_marker_tocheck.rstrip(']')
        for marker_info in marker_infos:
            if marker_info[0] in atag_marker_tocheck or atag_marker_tocheck in marker_info[0]:
                extract_a_tag_marker = atag_marker.lstrip('#')
                extract_a_tag_marker = extract_a_tag_marker.rstrip('#')
                href_location = marker_info[1]
                if 'javascript:void(0)' in href_location:
                    href_location = href_location.rstrip('\n')
                    assemblied_atag = '%s%s</a>' %  (href_location, extract_a_tag_marker)
                else:
                    href_location = href_location.rstrip('\n')
                    assemblied_atag = '<a href="%s">%s</a>' %  (href_location, extract_a_tag_marker)
                s = s.replace(atag_marker, assemblied_atag)
            elif marker_info[2] in atag_marker_tocheck or atag_marker_tocheck in marker_info[2]:
                extract_a_tag_marker = marker_info[0].lstrip('#')
                extract_a_tag_marker = extract_a_tag_marker.rstrip('#')
                href_location = marker_info[1]
                if 'javascript:void(0)' in href_location:
                    href_location = href_location.rstrip('\n')
                    assemblied_atag = '%s%s</a>' %  (href_location, extract_a_tag_marker)
                else:
                    href_location = href_location.rstrip('\n')
                    assemblied_atag = '<a href="%s">%s</a>' %  (href_location, extract_a_tag_marker)
                s = s.replace(atag_marker, assemblied_atag)
            else:
                pass
    return s

class RecoveryATag(Node):
    def __init__(self, nodelist):
        self.nodelist = nodelist

    def render(self, context):
        """
        """
        template_name = context.template_name
        h2t_records_path = os.path.join(settings.BASE_DIR, 'htmlataghref.h2t')
        h2t_records = []
        with open(h2t_records_path, 'r', encoding='utf-8') as h2t:
            for single_line in h2t:
                if "||" in single_line:
                    lines_infos = single_line.split('||')
                    template_name_low = template_name.lower()
                    line_info0_low = lines_infos[0].lower()
                    if template_name_low.find("\\") != -1:
                        template_name_low = template_name_low.replace("\\", "/")
                    if (template_name_low in line_info0_low or line_info0_low in template_name_low) and 'a' in lines_infos[1]:
                        ro_translate_puretext = lines_infos[2]
                        translated_text = _(ro_translate_puretext)
                        href_location = lines_infos[4]
                        h2t_records.append((translated_text, href_location, ro_translate_puretext))
                    else:
                        pass
                else:
                    pass
        

        return fancy_utility_function(self.nodelist.render(context).strip(), h2t_records)
