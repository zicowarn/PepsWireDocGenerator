import os
import django
import json
from django.template.loader import get_template, render_to_string  # @UnusedImport
from bs4 import BeautifulSoup

try:
    from myapp import settings  # @UnusedImport
except:
    pass

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "myapp.settings")
django.setup()

"""
本py模块将 hhc文件转换成 navimenu.py， 用于调试翻译的页面。
"""

def convert_to_dict(html_content):
    soup = BeautifulSoup(html_content, 'html.parser')

    def process_object(obj):
        obj_dict = {}
        for param in obj.find_all('param'):
            param_name = param.get('name')
            param_value = param.get('value')
            obj_dict[param_name] = param_value
        return obj_dict

    def process_ul(ul):
        result = {}
        if ul:
            for li in ul.find_all('li'):
                site_object = li.find('object', {'type': 'text/sitemap'})
                if site_object:
                    site_dict = process_object(site_object)
                    site_name = site_dict.get('Name')
                    site_url = site_dict.get('Local', '#')
                    fixed_url = site_url.replace("ä", "ae")
                    fixed_url = fixed_url.replace("Ä", "Ae")
                    fixed_url = fixed_url.replace("ö", "oe")
                    fixed_url = fixed_url.replace("Ö", "Oe")
                    fixed_url = fixed_url.replace("ü", "ue")
                    fixed_url = fixed_url.replace("Ü", "Ue")
                    fixed_url = fixed_url.replace("ß", "ss")
                    fixed_url = fixed_url.replace("&auml;", "ae")
                    fixed_url = fixed_url.replace("&Auml;", "Ae")
                    fixed_url = fixed_url.replace("&ouml;", "oe")
                    fixed_url = fixed_url.replace("&Ouml;", "Oe")
                    fixed_url = fixed_url.replace("&uuml;", "ue")
                    fixed_url = fixed_url.replace("&Uuml;", "Ue")
                    fixed_url = fixed_url.replace("&szlig;", "ss")
                    result[site_name] = {'url': fixed_url, 'children': process_ul(li.find('ul'))}
        return result

    all_ul_elements = soup.find_all('ul')
    result_dict = {}
    for ul_element in all_ul_elements:
        result_dict.update(process_ul(ul_element))
    return result_dict

hhc_fullpath = os.path.join(settings.BASE_DIR, "asset", "086", "wire_xxx.hhc")
html_content = get_template(hhc_fullpath).render()
result_dict = convert_to_dict(html_content)
print(result_dict)

# 保存字典到文件
menu_fullpath = "source/myapp/navimenu.py"
# 定义变量名
variable_name = 'menus'
# 使用 f-string 格式化输出
formatted_output = f"{variable_name} = {json.dumps(result_dict, ensure_ascii=False, indent=2).encode().decode('utf-8')}"

with open(menu_fullpath, 'w', encoding='utf-8') as file:
    file.write(formatted_output)