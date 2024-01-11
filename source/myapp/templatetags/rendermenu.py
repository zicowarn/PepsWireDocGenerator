from django import template

register = template.Library()

@register.inclusion_tag('menuitem.html', takes_context=True)
def rendermenu(context, menulabel, menuvalue):
    return {
        'menulabel': menulabel,
        'menuvalue': menuvalue,
        'level': context.get('level', 1),
    }