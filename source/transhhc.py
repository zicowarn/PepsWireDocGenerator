import os
import collections
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
def extract_data(element):
    result = {}
    for item in element.find_all('li', recursive=False):
        name_param = item.find('param', {'name': 'Name'})
        print(f'### {name_param}')
        local_param = item.find('param', {'name': 'Local'})
        if name_param and local_param:
            site_url = local_param.get('Local', '#')
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
            site_url = fixed_url.replace("&szlig;", "ss")
            result[name_param['value']] = site_url
    for item in element.find_all('ul', recursive=False):
        # 处理嵌套的ul和li
        result.update(extract_data(item))
    return result

hhc_fullpath = os.path.join(settings.BASE_DIR, "asset", "086", "wire_xxx.hhc")
html_content = get_template(hhc_fullpath).render()
# 保存字典到文件
menu_fullpath = "./source/myapp/navimenu.html"
with open(menu_fullpath, 'w', encoding='utf-8') as file:
    file.write(html_content)

soup = BeautifulSoup(html_content, 'html.parser')

result_dict = extract_data(soup.find('html'))
print(result_dict)

# 保存字典到文件
menu_fullpath = "./source/myapp/navimenu2.py"
# 定义变量名
variable_name = 'menus'
# 使用 f-string 格式化输出
formatted_output = f"{variable_name} = {result_dict}"

with open(menu_fullpath, 'w', encoding='utf-8') as file:
    file.write(formatted_output)