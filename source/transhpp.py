from bs4 import BeautifulSoup

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
        for li in ul.find_all('li'):
            site_object = li.find('object', {'type': 'text/sitemap'})
            if site_object:
                site_dict = process_object(site_object)
                site_name = site_dict.get('Name')
                site_url = site_dict.get('Local', '#')
                result[site_name] = {'url': site_url, 'children': process_ul(li.find('ul'))}
        return result

    menus = process_ul(soup.find('ul'))
    return menus

html_content = """<html><!-- your HTML content here --></html>"""
result_dict = convert_to_dict(html_content)
print(result_dict)