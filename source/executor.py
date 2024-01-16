from __future__ import print_function
'''
Created on 21.06.2019
Updated on 10.01.2024

@author: wang
'''
import os
import sys
import re
import codecs
import shutil
import signal

from lxml import html, etree
from xml.etree import ElementTree
import bs4
from bs4 import BeautifulSoup
from selenium import webdriver

import django
from django.template import Template, Context
from django.template.engine import Engine
from django.shortcuts import render  # @UnusedImport
from django.template.loader import get_template, render_to_string  # @UnusedImport
from django.utils.translation import ugettext_lazy as _  # @UnusedImport
try:
    from myapp import settings  # @UnusedImport
except:
    pass
from django.utils import translation

PRINT_DEBUG = True
CHM_CHECK_STATIC_SUBFOLDER = True
CHM_TRANSLATE_CONTRY_CODES = {
    'zh-hans':"086",
    'en-us':"044",
    'de-de':"049",
}
CHM_FILES_CODING_LIST = {
    "086": "gb2312",
    "044": "cp1252",
    "049": "cp1252"

}

TRANSCODE_FROM = "cp1252"
TRANSCODE_TO = "utf-8"


CHM_HHK_TEMPLATE = "wire_xxx.hhk"
CHM_HHC_TEMPLATE = "wire_xxx.hhc"
CHM_HHP_TEMPLATE = "wire_xxx.hhp"
CHM_BRS_TEMPLATE = "wire_xxx.brs"
CHM_LNG_TEMPLATE = "RoboHHRE_xxx.lng"
TEMPALTES_BASE_PATH = os.path.join(settings.BASE_DIR, "templates")
CHM_EXTRA_BASE_PATH = os.path.join(settings.BASE_DIR, "asset")
CHM_STATC_BASE_PATH = os.path.join(settings.BASE_DIR, "static")
CHM_BUILD_BASE_PATH = os.path.join("D:\Eclipse-Works\workspace\\PepsWireDocGenerator", "build")

SELENIUM_DRIVER_LOCATION = "/Users/mrwang/workspace/1-no-project/chromedriver"
H2T_RECORD_A_TAG_HREF = os.path.join("D:\Eclipse-Works\workspace\\PepsWireDocGenerator\\source", "htmlataghref.h2t")


DEMO_1 = '''
{% extends "base.html" %}
{% load i18n %}
{% load linebreakless %}{% linebreakless %}
<!--Head Title -->
{% block headtitle %}
'''
DEMO_2 = "    <TITLE>{0}</TITLE>"

DEMO_3 = '''
{% endblock %}
<!--/ Head Title -->
<!-- Head CSS-->
{% block headcss %}
'''

DEMO_4 ='''    <LINK rel="StyleSheet" href="{0}"/>
    {1}'''

DEMO_4_EXTEND = '''    
        span {
                font-weight: bold;
            }
        
        .pitalic { 
            margin-top:0; 
            margin-bottom:0; 
            font-style: italic;
            color:#FF0000;
        }
    '''

DEMO_4_DEFAULT = '''    <style type="text/css">
        span {
                font-weight: bold;
            }
        .pitalic { 
            margin-top:0; 
            margin-bottom:0; 
            font-style: italic;
            color:#FF0000;
        }
    </style>'''

DEMO_5 ='''
{% endblock %}
<!--/ Head CSS -->
<!-- Head JavaScript -->
{% block headjs %}
    <SCRIPT LANGUAGE="JavaScript" TITLE="BSSC Special Effects" SRC="../ehlpdhtm.js"></SCRIPT>
{% endblock %}
<!--/ Head JavaScript -->
{% block mainbody %}
'''

DEMO_6 = '''    {0}'''

DEMO_7 = '''
{% endblock %}
{% endlinebreakless %}
'''


os.environ.setdefault("DJANGO_SETTINGS_MODULE", "myapp.settings")

django.setup()


########################################
# Test functions                       # 
########################################
def test():
    template_string = "Hello {{ name }}"
    template = Template(template_string, engine=Engine())
    context = Context({"name": "world"})
    output = template.render(context) #"hello world"
    print(output)


def test_case():
    import doctest
    #doctest.testmod
    doctest.run_docstring_examples(translate_templates_and_export, globals())


########################################
# Init functions                       # 
########################################
def init_project():
    """[summary]
    """
    pass


########################################
# Collect functions                     # 
########################################
def collect_all_static_files():
    """Please run it in source folder
    
    'xcopy "..\origin\*.*" "..\source\static\*.*" /h/i/c/k/r/y/s /exclude:.static-all-ignore'
    """
    current_path, current_file = os.path.split(os.path.realpath(__file__))
    if "source" in current_path:
        source_path = current_path.replace('source', 'origin')
        destination_path = os.path.join(current_path, 'static')
        ignore_file =os.path.join(current_path.replace('source', 'extra'), '.static-all-ignore')
    elif "extra" in current_path:
        source_path = current_path.replace('extra', 'origin')
        destination_path = os.path.join(current_path.replace('extra', 'source'), 'static')
        ignore_file = os.path.join(current_path, 'static-all-ignore')
    else:
        return
    os.system(f'xcopy "{source_path}\*.*" "{destination_path}\*.*" /h/i/c/k/r/y/s /exclude:{ignore_file}')


def collect_js_static_files():
    """Please run it in source folder
    
    'xcopy "..\origin\*.*" "..\source\static\*.*" /h/i/c/k/r/y/s /exclude:.static-js-only-ignore'
    """
    current_path, current_file = os.path.split(os.path.realpath(__file__))
    if "source" in current_path:
        source_path = current_path.replace('source', 'origin')
        destination_path = os.path.join(current_path, 'static')
        ignore_file =os.path.join(current_path.replace('source', 'extra'), '.static-js-only-ignore')
    elif "extra" in current_path:
        source_path = current_path.replace('extra', 'origin')
        destination_path = os.path.join(current_path.replace('extra', 'source'), 'static')
        ignore_file = os.path.join(current_path, 'static-all-ignore')
    else:
        return
    os.system(f'xcopy "{source_path}\*.*" "{destination_path}\*.*" /h/i/c/k/r/y/s /exclude:{ignore_file}')

def collect_htm_files():
    """Please run it in source folder
    
    'xcopy "..\origin\*.*" "..\source\templates\*.*" /h/i/c/k/r/y/s /exclude:.templates-all-ignore'
    """
    current_path, current_file = os.path.split(os.path.realpath(__file__))
    if "source" in current_path:
        source_path = current_path.replace('source', 'origin')
        destination_path = os.path.join(current_path, 'templates')
        ignore_file =os.path.join(current_path.replace('source', 'extra'), '.templates-all-ignore')
    elif "extra" in current_path:
        source_path = current_path.replace('extra', 'origin')
        destination_path = os.path.join(current_path.replace('extra', 'source'), 'templates')
        ignore_file = os.path.join(current_path, 'static-all-ignore')
    else:
        return
    os.system(f'xcopy "{source_path}\*.*" "{destination_path}\*.*" /h/i/c/k/r/y/s /exclude:{ignore_file}')


########################################
# convert：convert htm to template     # 
########################################
orig_prettify = bs4.BeautifulSoup.prettify
r = re.compile(r'^(\s*)', re.MULTILINE)
def prettify(self, encoding=None, formatter="minimal", indent_width=4):
    """[summary]

    Args:
        encoding ([type], optional): [description]. Defaults to None.
        formatter (str, optional): [description]. Defaults to "minimal".
        indent_width (int, optional): [description]. Defaults to 4.

    Returns:
        [type]: [description]
    """
    return r.sub(r'\1' * indent_width, orig_prettify(self, encoding, formatter))
bs4.BeautifulSoup.prettify = prettify


def rreplace(s, old, new, occurrence):
    li = s.rsplit(old, occurrence)
    return new.join(li)

def involk_handler(root=None, rts=[], b_del=False):
    """[summary]

    Args:
        root ([type], optional): [description]. Defaults to None.
        rts (list, optional): [description]. Defaults to [].
        b_del (bool, optional): [description]. Defaults to False.
    """
    font_list = root.findall('font')
    a_list = root.findall('a')
    img_list = root.findall('img')
    span_list = root.findall('span')
    br_list = root.findall('br')
    b_list = root.findall('b')
    if len(font_list) != 0:
        rts[0] += 1
        for font_single in font_list:
            involk_handler(font_single, rts, b_del)
            if b_del == True:
                root.remove(font_single)
    if len(a_list) != 0:
        rts[1] += 1
        for a_single in a_list:
            involk_handler(a_single, rts, b_del)
            if b_del == True:
                root.remove(a_single)
    if len(img_list) != 0:
        rts[2] += 1
        for img_single in img_list:
            involk_handler(img_single, rts, b_del)
            if b_del == True:
                root.remove(img_single)
    if len(span_list) != 0:
        rts[3] += 1
        for span_single in span_list:
            involk_handler(span_single, rts, b_del)
            if b_del == True:
                root.remove(span_single)
    if len(b_list) != 0:
        rts[4] += 1
        for b_single in b_list:
            involk_handler(b_single, rts, b_del)
            if b_del == True:
                root.remove(b_single)
    if len(br_list) != 0:
        rts[5] += 1
        for br_single in br_list:
            involk_handler(br_single, rts, b_del)
            if b_del == True:
                root.remove(br_single)
    return 


def involk_tagbyname(root, tagname="a", rts=[]):
    """[summary]

    Args:
        root ([type]): [description]
        tagname (str, optional): [description]. Defaults to "a".
        rts (list, optional): [description]. Defaults to [].
    """
    tag_list = root.findall(tagname)
    if len(tag_list) != 0:
        for tag_single in tag_list:
            rts.append(tag_single)
            involk_tagbyname(tag_single, tagname, rts)
    else:
        fonts_list = root.findall('font')
        if len(fonts_list) != 0:
            for tag_single in fonts_list:
                # rts.append(tag_single)
                involk_tagbyname(tag_single, tagname, rts)
        spans_list = root.findall('span')
        if len(spans_list) != 0:
            for tag_single in spans_list:
                # rts.append(tag_single)
                involk_tagbyname(tag_single, tagname, rts)
    return


def convert_htm_to_template(str_relativ_path="", b_break_nextfile=False, b_break_nextfolder=False, b_auto_translate=False):
    """[summary]

    Args:
        str_relativ_path (str, optional): [description]. Defaults to "".
        b_break_nextfile (bool, optional): [description]. Defaults to False.
        b_break_nextfolder (bool, optional): [description]. Defaults to False.
        b_auto_translate (bool, optional): [description]. Defaults to False.

    Returns:
        [type]: [description]
    """
    driver_infos = None
    if os.path.exists(os.path.join(".", ".selenium-dirver-info")):
        with open(os.path.join(".", ".selenium-dirver-info"), 'r') as df:
            data = df.read()
            driver_infos = eval(data)
    if driver_infos != None:
        option = webdriver.ChromeOptions()
        option.add_argument('headless')
        executor_url = 'http://127.0.0.1:%s' % driver_infos['port']
    # not transfer htm file
    no_trans_filelist = []
    str_relativ_path = str_relativ_path.replace(' ', '')
    # traverse the list 
    for root, dirs, files in os.walk(os.path.join(TEMPALTES_BASE_PATH, str_relativ_path), topdown=False):
        if len(files) != 0:
            # variable of target file
            target_file = ""
            # iterate the files list
            for single_file in list(sorted(files)):
                # convert only htm files
                if not single_file.endswith('htm'):
                    continue
                # breakpoint set-point
                if "Disable_operation.htm" in single_file:
                    a = 0
                # set target path
                target_file = os.path.join(root, single_file)
                # 
                try:
                    # init html content variable 
                    htmlconent = ""
                    # relavant path to template base
                    relevant_base = re.sub(re.escape(TEMPALTES_BASE_PATH), '', root)
                    # read html content
                    with open(os.path.join(root, single_file), 'r', encoding='utf-8') as fss:
                        htmlconent = fss.read()
                    # check the html content, if already transfered, ignore it
                    if "{%" in htmlconent:
                        continue
                    
                    # outout infos
                    print('='*10)
                    print(target_file)
                    print('='*10)

                    # set processing flas
                    b_process = True
                    # set processed flas
                    b_processed = False

                    # convert html content to html element document object
                    htmldoc = html.fromstring(htmlconent)
                    
                    # get head tile string
                    headtitle = htmldoc.head.find('title').text
                    # replace some danger characters
                    headtitle = headtitle.replace("/", "&sol;")

                    # get head link definition
                    if htmldoc.head.find('link') != None:
                        headlink = htmldoc.head.find('link').get('href')
                    else:
                        headlink = ""

                    # get head inline style definition
                    headstyle = htmldoc.head.find('style')
                    headstyle_str = ""
                    # replace some danger characters
                    if headstyle != None:
                        headstyle_str = etree.tostring(headstyle).decode()
                        headstyle_str = headstyle_str.replace("&lt;", "<")
                        headstyle_str = headstyle_str.replace("&gt;", ">")
                        headstyle_str = rreplace(headstyle_str, "\n", "", 1)
                        headstyle_str = headstyle_str.replace("\n", "\n    ")
                    else:
                        headstyle_str = ""
                    
                    ### body part
                    if True: # 新模型中，不在翻译body，添加一个dummy作为未翻译的标识。
                        # 创建一个新的 <p> 元素
                        new_p = soup.new_tag("p")
                        new_p.string = '{% trans "no translated" %}'

                        # 直接在 <body> 中插入 <p> 元素
                        htmldoc.body.insert(0, new_p)
                        #
                        b_processed = True
                    else:
                        # handle all h1 tags
                        h1_lists = htmldoc.body.findall('h1')
                        for idx, h1_single in enumerate(h1_lists):
                            # get h2 text 
                            h1_text = h1_single.text or ''
                            # check h2 text
                            if h1_text.replace(' ', '') != '' and h1_text.replace('\xa0', '') != '':
                                # remove newline symbols
                                h1_text = h1_text.replace('\n', '')
                                # set translation flag
                                h1_newtext = '{% trans "' + h1_text + '" %}'
                                h1_single.text = h1_newtext

                        # handle all h2 tags
                        h2_lists = htmldoc.body.findall('h2')
                        for idx, h2_single in enumerate(h2_lists):
                            # get h2 text 
                            h2_text = h2_single.text or ''
                            # check h2 text
                            if h2_text.replace(' ', '') != '' and h2_text.replace('\xa0', '') != '':
                                # remove newline symbols
                                h2_text = h2_text.replace('\n', '')
                                # set translation flag
                                h2_newtext = '{% trans "' + h2_text + '" %}'
                                # reset the text of h2
                                h2_single.text = h2_newtext
                            else:
                                # get img sub tag of h2
                                h2_img_list = h2_single.findall('img')
                                # get a tag html string
                                h2_new_text = etree.tostring(h2_single, encoding="utf-8").decode('utf-8')
                                if len(h2_img_list) >= 1: # h2>img + text
                                    for h2_img in h2_img_list:
                                        h2_img_attrib = h2_img.attrib
                                        with open(H2T_RECORD_A_TAG_HREF, 'a', encoding='utf-8') as h2tfile:
                                            new_record = os.path.join(relevant_base, single_file) + "||" + 'img||' + str(h2_img_attrib) + "\n"
                                            h2tfile.write(new_record)
                                        h2_single.remove(h2_img)
                                    # remove img sub tag text
                                    h2_new_text = h2_new_text.replace('\n', '')
                                    # replace multi spaces to single space
                                    h2_new_text = " ".join(h2_new_text.split())
                                    #replace img tag to @
                                    h2_new_text = re.sub("""<img[\sa-zA-Z0-9="'.:;/_-]*>""", '@', h2_new_text)
                                    #repalce " into '
                                    h2_new_text = h2_new_text.replace('"', "'")
                                    h2_new_text = re.sub('</h2>', '', h2_new_text)
                                    h2_new_text = re.sub("""<h2[\sa-zA-Z0-9="'#&.:;/_-]*>""", '', h2_new_text)
                                    # add the translate flag
                                    h2_new_text = h2_new_text.lstrip()
                                    h2_new_text = h2_new_text.rstrip()
                                    h2_check_text = h2_new_text.replace("X", '')
                                    h2_check_text = h2_check_text.replace(" ", '')
                                    if h2_check_text != "" and "XXX" != h2_check_text:
                                        h2_single.text = '{% trans "' + h2_new_text + '" %}'
                                    else:
                                        pass

                        # handle all h3 tags
                        h3_lists = htmldoc.body.findall('h3')
                        for idx, h3_single in enumerate(h3_lists):
                            h3_text = h3_single.text or ''
                            if h3_text.replace(' ', '') != '' and h3_text.replace('\xa0', '') != '':
                                h3_text = h3_text.replace('\n', '')
                                h3_newtext = '{% trans "' + h3_text + '" %}'
                                h3_single.text = h3_newtext
                        
                        ### case 1
                        # handle all body>p tags
                        p_lists = htmldoc.body.findall('p')
                        # 
                        for idx, p_single in enumerate(p_lists):
                            # set process flag
                            b_process = True
                            # set italic flag
                            b_full_italic = False
                            # get atrribs of p_single
                            p_attrib = p_single.attrib
                            # 
                            rts = [0]*6
                            involk_handler(p_single, rts, False)
                            # check if p tag has sub tags: font, a, b, br, or span 
                            if sum(rts[0:6]) != 0:
                                #
                                b_processed = True
                                # get text of p_single
                                p_text = p_single.text
                                
                                # get pure html code of p tag
                                p_tag_string = etree.tostring(p_single, encoding="utf-8").decode('utf-8')
                                # p tag has sub tag: font
                                if rts[0] != 0:
                                    if "font-style: italic;" in p_tag_string and rts[0] == 1:
                                        if p_text == None:
                                            b_full_italic = True
                                        else:
                                            b_full_italic = False
                                    else:
                                        b_full_italic = False
                                else:
                                    pass
                                
                                # in case, no font tags and no start-text of p tag
                                if p_text == None and rts[0] == 0:
                                    check_str = p_tag_string.replace('\n', '')
                                    check_str = check_str.replace('<br/>', ' ')
                                    check_str = check_str.replace('<br>', ' ')
                                    if len(check_str) <= 90:
                                        output_text = check_str[-50:-1]
                                    else:
                                        output_text = check_str[-50:-1]
                                    print('-'*40)
                                    print('Warning, danger handle the p <tag> : %s' % output_text)
                                    a_newlist =[]
                                    involk_tagbyname(p_single, 'a', a_newlist)
                                    b_newlist =[]
                                    involk_tagbyname(p_single, 'b', b_newlist)
                                    img_newlist = []
                                    involk_tagbyname(p_single, 'img', img_newlist)
                                    span_newlist = []
                                    involk_tagbyname(p_single, 'span', span_newlist)
                                    map_newlist = []
                                    involk_tagbyname(p_single, 'map', map_newlist)
                                    # get string before p close tag
                                    p_before_close = re.search("[\sa-zA-Z0-9()]*</p>$", check_str)
                                    # get matched string
                                    if p_before_close != None:
                                        # strip </p>
                                        p_before_close_string = p_before_close.group(0).rstrip('</p>')
                                    else:
                                        # set empty
                                        p_before_close_string = ''
                                    if len(a_newlist) != 0:
                                        b_process = True
                                    elif len(b_newlist) != 0:
                                        b_process = True
                                    elif len(span_newlist) != 0:
                                        b_process = True
                                    elif len(img_newlist) != 0 and p_before_close_string != '' and len(map_newlist) == 0:
                                        b_process = True
                                    else: #input_text = input("Press input any char to continous procsessing...")
                                        b_process = False
                                else:
                                    a = 0
                                # p tag has sub tag: a
                                if sum(rts[1:3]) != 0 and b_process == True:
                                    #
                                    b_processed = True
                                    # get a tags list
                                    a_newlist =[]
                                    involk_tagbyname(p_single, 'a', a_newlist)
                                    for a_new in a_newlist:
                                        a_new_text = a_new.text
                                        check_str = ''
                                        if a_new_text != None:
                                            # replace newline symbols
                                            check_str = a_new_text.replace('\n', '')
                                            # replace dobble spaces 
                                            check_str = check_str.replace(' ', '')
                                            # get a tag html string
                                            a_text = etree.tostring(a_new, encoding="utf-8").decode('utf-8')
                                            # remove newline char
                                            a_text = a_text.replace('\n', '')
                                            # replace multi spaces to single space
                                            a_text = " ".join(a_text.split())
                                            # move close tag and tail: </a>xxxx
                                            a_text = re.sub('</a>.*', '', a_text)
                                            # get a tag atrributes string
                                            a_new_attrib = re.search("""<a[\sa-zA-Z0-9="'.:&\)\(;/_-]*>{1}""", a_text)
                                            if a_new_attrib == None: 
                                                a_new_attrib = re.search("""<a[\sa-zA-Z0-9="\\'.,:&#\)\(;/_-]*>{1}""", a_text)
                                        else:
                                            pass
                                        if a_new_text == None or check_str == '':
                                            # get a tag html string
                                            a_new_text = etree.tostring(a_new, encoding="utf-8").decode('utf-8')
                                            # remove newline char
                                            a_new_text = a_new_text.replace('\n', '')
                                            # replace multi spaces to single space
                                            a_new_text = " ".join(a_new_text.split())
                                            # move close tag and tail: </a>xxxx
                                            a_new_text = re.sub('</a>.*', '', a_new_text)
                                            # get a tag atrributes string
                                            a_new_attrib = re.search("""<a[\sa-zA-Z0-9="'.:&\)\(;/_-]*>{1}""", a_new_text)
                                            if a_new_attrib == None: 
                                                a_new_attrib = re.search("""<a[\sa-zA-Z0-9="\\'.,:&\)\(;/_-]*>{1}""", a_new_text)
                                            # move open tag 
                                            a_new_text = re.sub("""<a[\sa-zA-Z0-9="\\'.,:&#\)\(;/_-]*>{1}""", '', a_new_text)
                                            # move child open tag <font>
                                            a_new_text = re.sub("""<font[\sa-zA-Z0-9="'&#.,!:;/_-]*>""", '', a_new_text)
                                            # move close tag
                                            a_new_text = re.sub('</font>', '', a_new_text)
                                            # move child open tag <span>
                                            a_new_text = re.sub("""<span[\sa-zA-Z0-9="'#.,!:;/_-]*>""", '', a_new_text)
                                            # move close tag
                                            a_new_text = re.sub('</span>', '', a_new_text)
                                        else:
                                            pass
                                            
                                        a_new_text = a_new_text.replace('\n', '')
                                        a_new_text = a_new_text.replace('<br/>', ' ')
                                        a_new_text = a_new_text.replace('<br>', ' ')
                                        a_new_text = a_new_text.lstrip()
                                        a_new_text = a_new_text.rstrip()
                                        a_new_text = " ".join(a_new_text.split())
                                        a_new_text = a_new_text.replace('"', "'")
                                        a_new_href = a_new.get('href') or ''
                                        a_new_tranlate_text = '{% trans "' + a_new_text + '" %}'
                                        with open(H2T_RECORD_A_TAG_HREF, 'a', encoding='utf-8') as h2tfile:
                                            if 'javascript:void' in a_new_href:
                                                a_new_href = a_new_attrib.group(0)
                                            elif a_new_href == None: # <a name="xxx" id="xxx"/>
                                                a_new_href = a_new_attrib.group(0)
                                            new_record = os.path.join(relevant_base, single_file) + "||" + 'a||' + a_new_text + "||" +  a_new_tranlate_text + "||" + a_new_href + "\n"
                                            h2tfile.write(new_record)
                                    img_newlist = []
                                    involk_tagbyname(p_single, 'img', img_newlist)
                                    for img_new in img_newlist:
                                        img_new_attrib = img_new.attrib
                                        with open(H2T_RECORD_A_TAG_HREF, 'a', encoding='utf-8') as h2tfile:
                                            new_record = os.path.join(relevant_base, single_file) + "||" + 'img||' + str(img_new_attrib) + "\n"
                                            h2tfile.write(new_record)
                                else:
                                    pass
                                
                                if b_process == True:
                                    # delete all sub tags, object levels
                                    involk_handler(p_single, [0]*6, True)
                                    # delete all sub tags, string levels
                                    p_tag_string = p_tag_string.replace('\n', '')
                                    p_tag_string = p_tag_string.replace('&#10;', '')
                                    p_tag_string = p_tag_string.replace('&#9;', ' ')
                                    p_tag_string = p_tag_string.replace('<br/>', ' ')
                                    p_tag_string = p_tag_string.replace('<br>', ' ')
                                    p_tag_string = " ".join(p_tag_string.split())
                                    # move some uncessary symbols : font
                                    p_tag_string = re.sub("""<font[\sa-zA-Z0-9="'&#.,!:;/_-]*>""", '[', p_tag_string)
                                    p_tag_string = re.sub('</font>', ']', p_tag_string)
                                    # move some uncessary symbols : span
                                    p_tag_string = re.sub("""<span[\sa-zA-Z0-9="'#.,!:;/_-]*>""", '[', p_tag_string)
                                    p_tag_string = re.sub('</span>', ']', p_tag_string)
                                    # move some uncessary symbols : b
                                    p_tag_string = re.sub("""<b[\sa-zA-Z0-9="'#.,!:;/_-]*>""", '[', p_tag_string)
                                    p_tag_string = re.sub('</b>', ']', p_tag_string)
                                    #replace img tag to @
                                    p_tag_string = re.sub("""<img[\sa-zA-Z0-9="'.:;/_-]*>""", '@', p_tag_string)
                                    #replace a tag to #
                                    p_tag_string = re.sub('</a>', '#', p_tag_string)
                                    #p_tag_string = re.sub("""<a[\sa-zA-Z0-9="'.:&\)\(;/_-]*>""", '#', p_tag_string)
                                    p_tag_string = re.sub("""<a[\sa-zA-Z0-9="\\'.,:&#\)\(;/_-]*>{1}""", '#', p_tag_string)
                                    #repalce " into '
                                    p_tag_string = p_tag_string.replace('"', "'")
                                    p_tag_string = re.sub('</p>', '', p_tag_string)
                                    p_tag_string = re.sub("""<p[\sa-zA-Z0-9="'#&.:;/_-]*>""", '', p_tag_string)
                                    # add the translate flag
                                    p_tag_string = p_tag_string.lstrip()
                                    p_tag_string = p_tag_string.rstrip()
                                    p_tag_check_string = p_tag_string.replace("X", '')
                                    p_tag_check_string = p_tag_check_string.replace(" ", '')
                                    if p_tag_check_string != "" and "XXX" != p_tag_string:
                                        p_single.text = '{% trans "' + p_tag_string + '" %}'
                                    # set class attribute of p tag
                                    if b_full_italic == True:
                                        p_single.classes |= ['pitalic']
                                    else:
                                        a = 0
                                else:
                                    p_tag_string = etree.tostring(p_single, encoding="utf-8").decode('utf-8')
                                    print('-'*40)
                                    if len(p_tag_string) > 80:
                                        print('Error, can not handle the p <tag> : %s' % p_tag_string[:79])
                                    else:
                                        print('Error, can not handle the p <tag> : %s' % p_tag_string)
                            else:
                                #
                                b_processed = True
                                # assume it has only texts
                                p_text = p_single.text
                                if p_text != None and p_text != "" and p_text != '\xa0':
                                    # move newlines symbols
                                    p_text = p_text.replace('\n', '')
                                    # move some uncessary symbols : br
                                    p_text = p_text.replace('<br/>', '')
                                    p_text = p_text.replace('<br>', '')
                                    # replace dobble spaces
                                    p_text = " ".join(p_text.split())
                                    #repalce " into '
                                    p_text = p_text.replace('"', "'")
                                    p_text = p_text.lstrip()
                                    p_text = p_text.rstrip()
                                    p_tag_check_string = p_text.replace("X", '')
                                    p_tag_check_string = p_tag_check_string.replace(" ", '')
                                    if p_tag_check_string != "" and "XXX" != p_text:
                                        p_newtext = '{% trans "' + p_text + '" %}'
                                        p_single.text = p_newtext
                                else:
                                    pass
                        
                        ### case 2
                        # handle all ul>li>p case
                        p_lists = htmldoc.body.findall('ul/li/p')

                        for idx, p_single in enumerate(p_lists):
                            # set process flag
                            b_process = True
                            # set italic flag
                            b_full_italic = False
                            # get atrribs of p_single
                            p_attrib = p_single.attrib
                            # 
                            rts = [0]*6
                            involk_handler(p_single, rts, False)
                            # check if p tag has sub tags: font, a, b, br, or span 
                            if sum(rts[0:6]) != 0:
                                #
                                b_processed = True
                                # get text of p_single
                                p_text = p_single.text
                                
                                # get pure html code of p tag
                                p_tag_string = etree.tostring(p_single, encoding="utf-8").decode('utf-8')
                                # p tag has sub tag: font
                                if rts[0] != 0:
                                    if "font-style: italic;" in p_tag_string and rts[0] == 1:
                                        if p_text == None:
                                            b_full_italic = True
                                        else:
                                            b_full_italic = False
                                    else:
                                        b_full_italic = False
                                else:
                                    pass
                                
                                # in case, no font tags and no start-text of p tag
                                if p_text == None and rts[0] == 0:
                                    check_str = p_tag_string.replace('\n', '')
                                    check_str = check_str.replace('<br/>', ' ')
                                    check_str = check_str.replace('<br>', ' ')
                                    if len(check_str) <= 90:
                                        output_text = check_str
                                    else:
                                        output_text = check_str[:90]
                                    print('-'*40)
                                    print('Warning, danger handle the p <tag> : %s' % output_text)
                                    a_newlist =[]
                                    involk_tagbyname(p_single, 'a', a_newlist)
                                    b_newlist =[]
                                    involk_tagbyname(p_single, 'b', b_newlist)
                                    img_newlist = []
                                    involk_tagbyname(p_single, 'img', img_newlist)
                                    span_newlist = []
                                    involk_tagbyname(p_single, 'span', span_newlist)
                                    map_newlist = []
                                    involk_tagbyname(p_single, 'map', map_newlist)
                                    # get string before p close tag
                                    p_before_close = re.search("[\sa-zA-Z0-9]*</p>$", check_str)
                                    # get matched string
                                    if p_before_close != None:
                                        # strip </p>
                                        p_before_close_string = p_before_close.group(0).rstrip('</p>')
                                    else:
                                        # set empty
                                        p_before_close_string = ''
                                    if len(a_newlist) != 0:
                                        b_process = True
                                    elif len(a_newlist) != 0:
                                        b_process = True
                                    elif len(span_newlist) != 0:
                                        b_process = True
                                    elif len(img_newlist) != 0 and p_before_close_string != '' and len(map_newlist) == 0:
                                        b_process = True
                                    else: #input_text = input("Press input any char to continous procsessing...")
                                        b_process = False
                                else:
                                    a = 0
                                # p tag has sub tag: a
                                if sum(rts[1:3]) != 0 and b_process == True:
                                    #
                                    b_processed = True
                                    # get a tags list
                                    a_newlist =[]
                                    involk_tagbyname(p_single, 'a', a_newlist)
                                    for a_new in a_newlist:
                                        a_new_text = a_new.text
                                        check_str = ''
                                        if a_new_text != None:
                                            # replace newline symbols
                                            check_str = a_new_text.replace('\n', '')
                                            # replace dobble spaces 
                                            check_str = check_str.replace(' ', '')
                                            # get a tag html string
                                            a_text = etree.tostring(a_new, encoding="utf-8").decode('utf-8')
                                            # remove newline char
                                            a_text = a_text.replace('\n', '')
                                            # replace multi spaces to single space
                                            a_text = " ".join(a_text.split())
                                            # move close tag and tail: </a>xxxx
                                            a_text = re.sub('</a>.*', '', a_text)
                                            # get a tag atrributes string
                                            a_new_attrib = re.search("""<a[\sa-zA-Z0-9="'.:&\)\(;/_-]*>{1}""", a_text)
                                            if a_new_attrib == None: 
                                                a_new_attrib = re.search("""<a[\sa-zA-Z0-9="\\'.,:&#\)\(;/_-]*>{1}""", a_text)
                                        else:
                                            pass
                                        if a_new_text == None or check_str == '':
                                            # get a tag html string
                                            a_new_text = etree.tostring(a_new, encoding="utf-8").decode('utf-8')
                                            # remove newline char
                                            a_new_text = a_new_text.replace('\n', '')
                                            # replace multi spaces to single space
                                            a_new_text = " ".join(a_new_text.split())
                                            # move close tag and tail: </a>xxxx
                                            a_new_text = re.sub('</a>.*', '', a_new_text)
                                            # get a tag atrributes string
                                            a_new_attrib = re.search("""<a[\sa-zA-Z0-9="'.:&\)\(;/_-]*>{1}""", a_new_text)
                                            if a_new_attrib == None: 
                                                a_new_attrib = re.search("""<a[\sa-zA-Z0-9="\\'.,:&#\)\(;/_-]*>{1}""", a_new_text)
                                            # move open tag 
                                            a_new_text = re.sub("""<a[\sa-zA-Z0-9="\\'.,:&\)\(;/_-]*>{1}""", '', a_new_text)
                                            # move child open tag <font>
                                            a_new_text = re.sub("""<font[\sa-zA-Z0-9="'&#.,!:;/_-]*>""", '', a_new_text)
                                            # move close tag
                                            a_new_text = re.sub('</font>', '', a_new_text)
                                            # move child open tag <span>
                                            a_new_text = re.sub("""<span[\sa-zA-Z0-9="'#.,!:;/_-]*>""", '', a_new_text)
                                            # move close tag
                                            a_new_text = re.sub('</span>', '', a_new_text)
                                        else:
                                            pass
                                            
                                        a_new_text = a_new_text.replace('\n', '')
                                        a_new_text = a_new_text.replace('<br/>', ' ')
                                        a_new_text = a_new_text.replace('<br>', ' ')
                                        a_new_text = a_new_text.lstrip()
                                        a_new_text = a_new_text.rstrip()
                                        a_new_text = " ".join(a_new_text.split())
                                        a_new_text = a_new_text.replace('"', "'")
                                        a_new_href = a_new.get('href') or ''
                                        a_new_tranlate_text = '{% trans "' + a_new_text + '" %}'
                                        with open(H2T_RECORD_A_TAG_HREF, 'a', encoding='utf-8') as h2tfile:
                                            if 'javascript:void' in a_new_href:
                                                a_new_href = a_new_attrib.group(0)
                                            elif a_new_href == '': # <a name="xxx" id="xxx"/>
                                                a_new_href = a_new_attrib.group(0)
                                            new_record = os.path.join(relevant_base, single_file) + "||" + 'a||' + a_new_text + "||" +  a_new_tranlate_text + "||" + a_new_href + "\n"
                                            h2tfile.write(new_record)
                                    img_newlist = []
                                    involk_tagbyname(p_single, 'img', img_newlist)
                                    for img_new in img_newlist:
                                        img_new_attrib = img_new.attrib
                                        with open(H2T_RECORD_A_TAG_HREF, 'a', encoding='utf-8') as h2tfile:
                                            new_record = os.path.join(relevant_base, single_file) + "||" + 'img||' + str(img_new_attrib) + "\n"
                                            h2tfile.write(new_record)
                                else:
                                    pass
                                
                                if b_process == True:
                                    # delete all sub tags, object levels
                                    involk_handler(p_single, [0]*6, True)
                                    # delete all sub tags, string levels
                                    p_tag_string = p_tag_string.replace('\n', '')
                                    p_tag_string = p_tag_string.replace('&#10;', '')
                                    p_tag_string = p_tag_string.replace('&#9;', ' ')
                                    p_tag_string = p_tag_string.replace('<br/>', ' ')
                                    p_tag_string = p_tag_string.replace('<br>', ' ')
                                    p_tag_string = " ".join(p_tag_string.split())
                                    # move some uncessary symbols : font
                                    p_tag_string = re.sub("""<font[\sa-zA-Z0-9="'&#.,!:;/_-]*>""", '[', p_tag_string)
                                    p_tag_string = re.sub('</font>', ']', p_tag_string)
                                    # move some uncessary symbols : span
                                    p_tag_string = re.sub("""<span[\sa-zA-Z0-9="'#.,!:;/_-]*>""", '[', p_tag_string)
                                    p_tag_string = re.sub('</span>', ']', p_tag_string)
                                    # move some uncessary symbols : b
                                    p_tag_string = re.sub("""<b[\sa-zA-Z0-9="'#.,!:;/_-]*>""", '[', p_tag_string)
                                    p_tag_string = re.sub('</b>', ']', p_tag_string)
                                    #replace img tag to @
                                    p_tag_string = re.sub("""<img[\sa-zA-Z0-9="'.:;/_-]*>""", '@', p_tag_string)
                                    #replace a tag to #
                                    p_tag_string = re.sub('</a>', '#', p_tag_string)
                                    #p_tag_string = re.sub("""<a[\sa-zA-Z0-9="'.:&\)\(;/_-]*>""", '#', p_tag_string)
                                    p_tag_string = re.sub("""<a[\sa-zA-Z0-9="\\'.,:&#\)\(;/_-]*>{1}""", '#', p_tag_string)
                                    #repalce " into '
                                    p_tag_string = p_tag_string.replace('"', "'")
                                    p_tag_string = re.sub('</p>', '', p_tag_string)
                                    p_tag_string = re.sub("""<p[\sa-zA-Z0-9="'#&.:;/_-]*>""", '', p_tag_string)
                                    # add the translate flag
                                    p_tag_string = p_tag_string.lstrip()
                                    p_tag_string = p_tag_string.rstrip()
                                    p_tag_check_string = p_tag_string.replace("X", '')
                                    p_tag_check_string = p_tag_check_string.replace(" ", '')
                                    if p_tag_check_string != "" and "XXX" != p_tag_string:
                                        p_single.text = '{% trans "' + p_tag_string + '" %}'
                                    # set class attribute of p tag
                                    if b_full_italic == True:
                                        p_single.classes |= ['pitalic']
                                    else:
                                        a = 0
                                else:
                                    p_tag_string = etree.tostring(p_single, encoding="utf-8").decode('utf-8')
                                    print('-'*40)
                                    if len(p_tag_string) > 80:
                                        print('Error, can not handle the p <tag> : %s' % p_tag_string[:79])
                                    else:
                                        print('Error, can not handle the p <tag> : %s' % p_tag_string)

                            else:
                                #
                                b_processed = True
                                # assume it has only texts
                                p_text = p_single.text
                                if p_text != None and p_text != "" and p_text != '\xa0':
                                    # move newlines symbols
                                    p_text = p_text.replace('\n', '')
                                    # move some uncessary symbols : br
                                    p_text = p_text.replace('<br/>', '')
                                    p_text = p_text.replace('<br>', '')
                                    # replace dobble spaces
                                    p_text = " ".join(p_text.split())
                                    #repalce " into '
                                    p_text = p_text.replace('"', "'")
                                    p_text = p_text.lstrip()
                                    p_text = p_text.rstrip()
                                    p_tag_check_string = p_text.replace("X", '')
                                    p_tag_check_string = p_tag_check_string.replace(" ", '')
                                    if p_tag_check_string != "" and "XXX" != p_text:
                                        p_newtext = '{% trans "' + p_text + '" %}'
                                        p_single.text = p_newtext
                                else:
                                    pass
                        
                        ### case 3
                        # handle all ol>li>p case
                        p_lists = htmldoc.body.findall('ol/li/p')

                        for idx, p_single in enumerate(p_lists):
                            # set process flag
                            b_process = True
                            # set italic flag
                            b_full_italic = False
                            # get atrribs of p_single
                            p_attrib = p_single.attrib
                            # 
                            rts = [0]*6
                            involk_handler(p_single, rts, False)
                            # check if p tag has sub tags: font, a, b, br, or span 
                            if sum(rts[0:6]) != 0:
                                #
                                b_processed = True
                                # get text of p_single
                                p_text = p_single.text
                                
                                # get pure html code of p tag
                                p_tag_string = etree.tostring(p_single, encoding="utf-8").decode('utf-8')
                                # p tag has sub tag: font
                                if rts[0] != 0:
                                    if "font-style: italic;" in p_tag_string and rts[0] == 1:
                                        if p_text == None:
                                            b_full_italic = True
                                        else:
                                            b_full_italic = False
                                    else:
                                        b_full_italic = False
                                else:
                                    pass
                                
                                # in case, no font tags and no start-text of p tag
                                if p_text == None and rts[0] == 0:
                                    check_str = p_tag_string.replace('\n', '')
                                    check_str = check_str.replace('<br/>', ' ')
                                    check_str = check_str.replace('<br>', ' ')
                                    if len(check_str) <= 90:
                                        output_text = check_str
                                    else:
                                        output_text = check_str[:90]
                                    print('-'*40)
                                    print('Warning, danger handle the p <tag> : %s' % output_text)
                                    a_newlist =[]
                                    involk_tagbyname(p_single, 'a', a_newlist)
                                    b_newlist =[]
                                    involk_tagbyname(p_single, 'b', b_newlist)
                                    img_newlist = []
                                    involk_tagbyname(p_single, 'img', img_newlist)
                                    span_newlist = []
                                    involk_tagbyname(p_single, 'span', span_newlist)
                                    map_newlist = []
                                    involk_tagbyname(p_single, 'map', map_newlist)
                                    # get string before p close tag
                                    p_before_close = re.search("[\sa-zA-Z0-9]*</p>$", check_str)
                                    # get matched string
                                    if p_before_close != None:
                                        # strip </p>
                                        p_before_close_string = p_before_close.group(0).rstrip('</p>')
                                    else:
                                        # set empty
                                        p_before_close_string = ''
                                    if len(a_newlist) != 0:
                                        b_process = True
                                    elif len(a_newlist) != 0:
                                        b_process = True
                                    elif len(span_newlist) != 0:
                                        b_process = True
                                    elif len(img_newlist) != 0 and p_before_close_string != '' and len(map_newlist) == 0:
                                        b_process = True
                                    else: #input_text = input("Press input any char to continous procsessing...")
                                        b_process = False
                                else:
                                    a = 0
                                # p tag has sub tag: a
                                if sum(rts[1:3]) != 0 and b_process == True:
                                    #
                                    b_processed = True
                                    # get a tags list
                                    a_newlist =[]
                                    involk_tagbyname(p_single, 'a', a_newlist)
                                    for a_new in a_newlist:
                                        a_new_text = a_new.text
                                        check_str = ''
                                        if a_new_text != None:
                                            # replace newline symbols
                                            check_str = a_new_text.replace('\n', '')
                                            # replace dobble spaces 
                                            check_str = check_str.replace(' ', '')
                                            # get a tag html string
                                            a_text = etree.tostring(a_new, encoding="utf-8").decode('utf-8')
                                            # remove newline char
                                            a_text = a_text.replace('\n', '')
                                            # replace multi spaces to single space
                                            a_text = " ".join(a_text.split())
                                            # move close tag and tail: </a>xxxx
                                            a_text = re.sub('</a>.*', '', a_text)
                                            # get a tag atrributes string
                                            a_new_attrib = re.search("""<a[\sa-zA-Z0-9="'.:&\)\(;/_-]*>{1}""", a_text)
                                            if a_new_attrib == None: 
                                                a_new_attrib = re.search("""<a[\sa-zA-Z0-9="\\'.,:&#\)\(;/_-]*>{1}""", a_text)
                                        else:
                                            pass
                                        if a_new_text == None or check_str == '':
                                            # get a tag html string
                                            a_new_text = etree.tostring(a_new, encoding="utf-8").decode('utf-8')
                                            # remove newline char
                                            a_new_text = a_new_text.replace('\n', '')
                                            # replace multi spaces to single space
                                            a_new_text = " ".join(a_new_text.split())
                                            # move close tag and tail: </a>xxxx
                                            a_new_text = re.sub('</a>.*', '', a_new_text)
                                            # get a tag atrributes string
                                            a_new_attrib = re.search("""<a[\sa-zA-Z0-9="'.:&\)\(;/_-]*>{1}""", a_new_text)
                                            if a_new_attrib == None: 
                                                a_new_attrib = re.search("""<a[\sa-zA-Z0-9="\\'.,:&#\)\(;/_-]*>{1}""", a_new_text)
                                            # move open tag 
                                            a_new_text = re.sub("""<a[\sa-zA-Z0-9="\\'.,:&\)\(;/_-]*>{1}""", '', a_new_text)
                                            # move child open tag <font>
                                            a_new_text = re.sub("""<font[\sa-zA-Z0-9="'&#.,!:;/_-]*>""", '', a_new_text)
                                            # move close tag
                                            a_new_text = re.sub('</font>', '', a_new_text)
                                            # move child open tag <span>
                                            a_new_text = re.sub("""<span[\sa-zA-Z0-9="'#.,!:;/_-]*>""", '', a_new_text)
                                            # move close tag
                                            a_new_text = re.sub('</span>', '', a_new_text)
                                        else:
                                            pass
                                            
                                        a_new_text = a_new_text.replace('\n', '')
                                        a_new_text = a_new_text.replace('<br/>', ' ')
                                        a_new_text = a_new_text.replace('<br>', ' ')
                                        a_new_text = a_new_text.lstrip()
                                        a_new_text = a_new_text.rstrip()
                                        a_new_text = " ".join(a_new_text.split())
                                        a_new_text = a_new_text.replace('"', "'")
                                        a_new_href = a_new.get('href') or ''
                                        a_new_tranlate_text = '{% trans "' + a_new_text + '" %}'
                                        with open(H2T_RECORD_A_TAG_HREF, 'a', encoding='utf-8') as h2tfile:
                                            if 'javascript:void' in a_new_href:
                                                a_new_href = a_new_attrib.group(0)
                                            elif a_new_href == '': # <a name="xxx" id="xxx"/>
                                                a_new_href = a_new_attrib.group(0)
                                            new_record = os.path.join(relevant_base, single_file) + "||" + 'a||' + a_new_text + "||" +  a_new_tranlate_text + "||" + a_new_href + "\n"
                                            h2tfile.write(new_record)
                                    img_newlist = []
                                    involk_tagbyname(p_single, 'img', img_newlist)
                                    for img_new in img_newlist:
                                        img_new_attrib = img_new.attrib
                                        with open(H2T_RECORD_A_TAG_HREF, 'a', encoding='utf-8') as h2tfile:
                                            new_record = os.path.join(relevant_base, single_file) + "||" + 'img||' + str(img_new_attrib) + "\n"
                                            h2tfile.write(new_record)
                                else:
                                    pass
                                
                                if b_process == True:
                                    # delete all sub tags, object levels
                                    involk_handler(p_single, [0]*6, True)
                                    # delete all sub tags, string levels
                                    p_tag_string = p_tag_string.replace('\n', '')
                                    p_tag_string = p_tag_string.replace('&#10;', '')
                                    p_tag_string = p_tag_string.replace('&#9;', ' ')
                                    p_tag_string = p_tag_string.replace('<br/>', ' ')
                                    p_tag_string = p_tag_string.replace('<br>', ' ')
                                    p_tag_string = " ".join(p_tag_string.split())
                                    # move some uncessary symbols : font
                                    p_tag_string = re.sub("""<font[\sa-zA-Z0-9="'&#.,!:;/_-]*>""", '[', p_tag_string)
                                    p_tag_string = re.sub('</font>', ']', p_tag_string)
                                    # move some uncessary symbols : span
                                    p_tag_string = re.sub("""<span[\sa-zA-Z0-9="'#.,!:;/_-]*>""", '[', p_tag_string)
                                    p_tag_string = re.sub('</span>', ']', p_tag_string)
                                    # move some uncessary symbols : b
                                    p_tag_string = re.sub("""<b[\sa-zA-Z0-9="'#.,!:;/_-]*>""", '[', p_tag_string)
                                    p_tag_string = re.sub('</b>', ']', p_tag_string)
                                    #replace img tag to @
                                    p_tag_string = re.sub("""<img[\sa-zA-Z0-9="'.:;/_-]*>""", '@', p_tag_string)
                                    #replace a tag to #
                                    p_tag_string = re.sub('</a>', '#', p_tag_string)
                                    #p_tag_string = re.sub("""<a[\sa-zA-Z0-9="'.:&\)\(;/_-]*>""", '#', p_tag_string)
                                    p_tag_string = re.sub("""<a[\sa-zA-Z0-9="\\'.,:&#\)\(;/_-]*>{1}""", '#', p_tag_string)
                                    #repalce " into '
                                    p_tag_string = p_tag_string.replace('"', "'")
                                    p_tag_string = re.sub('</p>', '', p_tag_string)
                                    p_tag_string = re.sub("""<p[\sa-zA-Z0-9="'#&.:;/_-]*>""", '', p_tag_string)
                                    # add the translate flag
                                    p_tag_string = p_tag_string.lstrip()
                                    p_tag_string = p_tag_string.rstrip()
                                    p_tag_check_string = p_tag_string.replace("X", '')
                                    p_tag_check_string = p_tag_check_string.replace(" ", '')
                                    if p_tag_check_string != "" and "XXX" != p_tag_string:
                                        p_single.text = '{% trans "' + p_tag_string + '" %}'
                                    # set class attribute of p tag
                                    if b_full_italic == True:
                                        p_single.classes |= ['pitalic']
                                    else:
                                        a = 0
                                else:
                                    p_tag_string = etree.tostring(p_single, encoding="utf-8").decode('utf-8')
                                    print('-'*40)
                                    if len(p_tag_string) > 80:
                                        print('Error, can not handle the p <tag> : %s' % p_tag_string[:79])
                                    else:
                                        print('Error, can not handle the p <tag> : %s' % p_tag_string)

                            else:
                                #
                                b_processed = True
                                # assume it has only texts
                                p_text = p_single.text
                                if p_text != None and p_text != "" and p_text != '\xa0':
                                    # move newlines symbols
                                    p_text = p_text.replace('\n', '')
                                    # move some uncessary symbols : br
                                    p_text = p_text.replace('<br/>', '')
                                    p_text = p_text.replace('<br>', '')
                                    # replace dobble spaces
                                    p_text = " ".join(p_text.split())
                                    #repalce " into '
                                    p_text = p_text.replace('"', "'")
                                    p_text = p_text.lstrip()
                                    p_text = p_text.rstrip()
                                    p_tag_check_string = p_text.replace("X", '')
                                    p_tag_check_string = p_tag_check_string.replace(" ", '')
                                    if p_tag_check_string != "" and "XXX" != p_text:
                                        p_newtext = '{% trans "' + p_text + '" %}'
                                        p_single.text = p_newtext
                                else:
                                    pass
                    

                    ### all cases would be handled
                    if not b_processed:
                        # append the non-handled files into list
                        no_trans_filelist.append(target_file)
                        # handle next file
                    else:
                        # convert body element object to body string
                        bodyxml_str = etree.tostring(htmldoc.body, encoding="utf-8").decode('utf-8')

                        # replace and delete some unnecessary part
                        bodyxml_str = re.sub('<script[\s\w=\/".>]+</script>', '', bodyxml_str, re.IGNORECASE)
                        bodyxml_str = re.sub('<script[\s\w=\/".>]+/>', '', bodyxml_str, re.IGNORECASE)
                        bodyxml_str = re.sub("<body>\n ", "", bodyxml_str, re.IGNORECASE)
                        bodyxml_str = re.sub("<body>", "", bodyxml_str, re.IGNORECASE)
                        bodyxml_str = re.sub("</body>\n\n\n", "", bodyxml_str, re.IGNORECASE)
                        bodyxml_str = re.sub("</body>\n\n", "", bodyxml_str, re.IGNORECASE)
                        bodyxml_str = re.sub("</body>\n", "", bodyxml_str, re.IGNORECASE)
                        bodyxml_str = re.sub("</body>", "", bodyxml_str, re.IGNORECASE)
                        bodyxml_str = re.sub("\n\n", "", bodyxml_str, re.IGNORECASE)
                        bodyxml_str = re.sub("\n", "", bodyxml_str, re.IGNORECASE)
                        bodyxml_str = re.sub("&#10;", "", bodyxml_str)
                        bodyxml_str = re.sub("&#9;", "", bodyxml_str)
                        
                        # set translate flag of head title
                        headtitle = headtitle.lstrip()
                        headtitle = headtitle.rstrip()
                        headtitle = '{% trans "' + headtitle + '" %}'
                        DEMO_2_SET = DEMO_2.format(headtitle)

                        # head link part
                        if headlink != "":
                            if headstyle_str != "":
                                # format css with params
                                DEMO_4_SET = DEMO_4.format(headlink, headstyle_str)
                                # 
                                additional_css = DEMO_4_EXTEND + "-->"
                                # 
                                DEMO_4_SET = DEMO_4_SET.replace("-->", additional_css)
                            else:
                                DEMO_4_SET = DEMO_4.format(headlink, DEMO_4_DEFAULT)
                        else:
                            DEMO_4_SET = DEMO_4_DEFAULT
                        
                        # html body part
                        if b_auto_translate == True:
                            # beauty html
                            soup = BeautifulSoup(bodyxml_str, 'html.parser')
                            DEMO_6_SET = DEMO_6.format(soup.prettify())
                        else:
                            DEMO_6_SET = DEMO_6.format(bodyxml_str)
                        
                        # write the converted file
                        with open(target_file, "w", encoding='utf-8') as newfile:
                            newfile.write(DEMO_1)
                            newfile.write(DEMO_2_SET)
                            newfile.write(DEMO_3)
                            newfile.write(DEMO_4_SET)
                            newfile.write(DEMO_5)
                            newfile.write(DEMO_6_SET)
                            newfile.write(DEMO_7)
                    
                    try:
                        driver = webdriver.Remote(command_executor=executor_url, desired_capabilities={}, options=option)
                        driver.close()   # this prevents the dummy browser
                        driver.session_id = driver_infos['session_id']
                        ### open in webbrower driver
                        js = "window.open('http://127.0.0.1:8000/%s/%s')" % (str_relativ_path, single_file)
                        driver.execute_script(js)
                        print("Viewer has open the template in the selenium driver: %s" % executor_url)
                    except:
                        print("Check whether the chrome selenium driver is running")
                except Exception as e:
                    import traceback
                    print(traceback.format_exc())
                
                if b_break_nextfile == True:
                    break
            if b_break_nextfile == True:
                break
        if b_break_nextfolder == True:
            break
    
    # finally reports
    if len(no_trans_filelist) > 0:
        print("*"*40)
    for file_path in no_trans_filelist:
        print(file_path)
    return True


########################################
# Transcode：Change file encoding      # 
########################################
def transcode_file(str_relativ_path="", b_folder_or_file=True, b_break_nextfile=False, b_break_nextfolder=False):
    """
    Transcode save the htm template, default is from cp1252 to utf-8,
    or specify the source encoding and the target encoding.

    Args:
        str_relativ_path (string): path/path with name, it relative of TEMPALTES_BASE_PATH 
        b_folder_or_file (boolean): default is true, it menas folder case
        b_break_nextfile (boolean): break the loop after handling one file
        b_break_nextfolder (boolean): break the loop after handling one folder

    Returns:
        [boolean]: [description]
    """
    if b_folder_or_file == True:
        for root, dirs, files in os.walk(os.path.join(TEMPALTES_BASE_PATH, str_relativ_path), topdown=False):
            if len(files) != 0:
                for single_file in files:
                    if not single_file.endswith('.htm'):
                        continue
                    target_file = os.path.join(root, single_file)
                    try:
                        htmlconent = ""
                        print("Converting encoding from %s to %s: %s" % (TRANSCODE_FROM, TRANSCODE_TO, target_file))
                        with open(target_file, 'r', encoding=TRANSCODE_FROM) as fss:
                            htmlconent = fss.read()
                        with open(target_file, 'w', encoding=TRANSCODE_TO) as fss:
                            fss.write(htmlconent)
                    except Exception as e:
                        print("Error Converting encoding from %s to %s: %s" % (TRANSCODE_FROM, TRANSCODE_TO, target_file))
                        print("Error details: %s" % e)
                    if b_break_nextfile == True:
                        break
                if b_break_nextfile == True:
                    break
            if b_break_nextfolder == True:
                break
        return True
    else:
        target_file = os.path.join(TEMPALTES_BASE_PATH, str_relativ_path)
        try:
            htmlconent = ""
            print("Converting encoding from %s to %s: %s" % (TRANSCODE_FROM, TRANSCODE_TO, target_file))
            with open(target_file, 'r', encoding=TRANSCODE_FROM) as fss:
                htmlconent = fss.read()
            with open(target_file, 'w', encoding=TRANSCODE_TO) as fss:
                fss.write(htmlconent)
            return True
        except Exception as e:
            print("Error Converting encoding from %s to %s: %s" % (TRANSCODE_FROM, TRANSCODE_TO, target_file))
            print("Error details: %s" % e)
            return False


########################################
# Fixinnerhref：Change href encoding   # 
########################################
def fix_innerhref_in_template(str_relativ_path="", b_folder_or_file=True, b_break_nextfile=False, b_break_nextfolder=False):
    """
    Fix the innerhref string, remove the specific german characters.

    Args:
        str_relativ_path (string): path/path with name, it relative of TEMPALTES_BASE_PATH 
        b_folder_or_file (boolean): default is true, it menas folder case
        b_break_nextfile (boolean): break the loop after handling one file
        b_break_nextfolder (boolean): break the loop after handling one folder

    Returns:
        [boolean]: [description]
    """
    if b_folder_or_file:
        for root, dirs, files in os.walk(os.path.join(TEMPALTES_BASE_PATH, str_relativ_path), topdown=False):
            if len(files) != 0:
                for single_file in files:
                    if not single_file.endswith('.htm'):
                        continue
                    target_file = os.path.join(root, single_file)
                    try:
                        htmlconent = ""
                        # assume, all htm is encoded with uft-8 now
                        print("Processing the htm: %s" % target_file)
                        with open(target_file, 'r', encoding='utf-8') as fss:
                            htmlconent = fss.read()
                        
                        tocheck_result = re.search('[öÖüÜäÄß]', htmlconent, re.IGNORECASE)
                        symbols_result = re.search('[&Auml;&auml;]', htmlconent, re.IGNORECASE)
                        findall_result = re.findall('(?<=href=").*(?=.htm)', htmlconent, re.IGNORECASE)
                        if (tocheck_result != None or symbols_result != None) and len(findall_result) != 0:
                            need_save = False
                            for single_result in findall_result:
                                fixed_result = single_result.replace("ä", "ae")
                                fixed_result = fixed_result.replace("Ä", "Ae")
                                fixed_result = fixed_result.replace("ö", "oe")
                                fixed_result = fixed_result.replace("Ö", "Oe")
                                fixed_result = fixed_result.replace("ü", "ue")
                                fixed_result = fixed_result.replace("Ü", "Ue")
                                fixed_result = fixed_result.replace("ß", "ss")
                                fixed_result = fixed_result.replace("&auml;", "ae")
                                fixed_result = fixed_result.replace("&Auml;", "Ae")
                                fixed_result = fixed_result.replace("&ouml;", "oe")
                                fixed_result = fixed_result.replace("&Ouml;", "Oe")
                                fixed_result = fixed_result.replace("&uuml;", "ue")
                                fixed_result = fixed_result.replace("&Uuml;", "Ue")
                                fixed_result = fixed_result.replace("&szlig;", "ss")
                                fixed_result.encode('ascii')
                                if fixed_result != single_result:
                                    print("Processing href (case 1) form: %s to %s" % (single_result, fixed_result))
                                    htmlconent = htmlconent.replace(single_result, fixed_result, 1)
                                    need_save = True
                            if need_save == True:
                                with open(target_file, 'w', encoding='utf-8') as fss:
                                    fss.write(htmlconent)
                                print("Saved the processed (case 1) changeds: %s" % target_file)
                        else:
                            pass
                        print("Successfully processed: %s" % target_file)
                    except Exception as e:
                        print("Error processing the htm: %s" % target_file)
                        print("Error details: %s" % e)
                    if b_break_nextfile == True:
                        break
                if b_break_nextfile == True:
                        break
            if b_break_nextfolder == True:
                break
        return True
    else:
        target_file = os.path.join(TEMPALTES_BASE_PATH, str_relativ_path)
        try:
            htmlconent = ""
            # assume, all htm is encoded with uft-8 now
            print("Processing the htm: %s" % target_file)
            with open(target_file, 'r', encoding='utf-8') as fss:
                htmlconent = fss.read()
            
            tocheck_result = re.search('[öÖüÜäÄß]', htmlconent, re.IGNORECASE)
            symbols_result = re.search('[&Auml;&auml;]', htmlconent, re.IGNORECASE)
            findall_result = re.findall('(?<=href=").*(?=.htm)', htmlconent, re.IGNORECASE)
            if (tocheck_result != None or symbols_result != None) and len(findall_result) != 0:
                need_save = False
                for single_result in findall_result:
                    fixed_result = single_result.replace("ä", "ae")
                    fixed_result = fixed_result.replace("Ä", "Ae")
                    fixed_result = fixed_result.replace("ö", "oe")
                    fixed_result = fixed_result.replace("Ö", "Oe")
                    fixed_result = fixed_result.replace("ü", "ue")
                    fixed_result = fixed_result.replace("Ü", "Ue")
                    fixed_result = fixed_result.replace("ß", "ss")
                    fixed_result = fixed_result.replace("&auml;", "ae")
                    fixed_result = fixed_result.replace("&Auml;", "Ae")
                    fixed_result = fixed_result.replace("&ouml;", "oe")
                    fixed_result = fixed_result.replace("&Ouml;", "Oe")
                    fixed_result = fixed_result.replace("&uuml;", "ue")
                    fixed_result = fixed_result.replace("&Uuml;", "Ue")
                    fixed_result = fixed_result.replace("&szlig;", "ss")
                    fixed_result.encode('ascii')
                    if fixed_result != single_result:
                        print("Processing href (case 1) form: %s to %s" % (single_result, fixed_result))
                        htmlconent = htmlconent.replace(single_result, fixed_result, 1)
                        need_save = True
                if need_save == True:
                    with open(target_file, 'w', encoding='utf-8') as fss:
                        fss.write(htmlconent)
                    print("Saved the processed (case 1) changeds: %s" % target_file)
            else:
                pass
            print("Successfully processed: %s" % target_file)
            return True
        except Exception as e:
            print("Error processing the htm: %s" % target_file)
            print("Error details: %s" % e)
            return False


########################################
# Fixfilename：Change template filename# 
########################################
def fix_filename_of_template(str_relativ_path="", b_break_nextfile=False, b_break_nextfolder=False):
    """
    Fix the filename of template files, rename/remove the specific german characters.

    Args:
        str_relativ_path (string): path/path with name, it relative of TEMPALTES_BASE_PATH
        b_break_nextfile (boolean): break the loop after handling one file
        b_break_nextfolder (boolean): break the loop after handling one folder

    Returns:
        [boolean]: [description]
    """
    tocheck_lines = []
    for root, dirs, files in os.walk(os.path.join(TEMPALTES_BASE_PATH, str_relativ_path), topdown=False):
        if len(files) != 0:
            for origin_filename in files:
                if not origin_filename.endswith('.htm'):
                    continue
                if "Disable_operation.htm" in origin_filename:
                    a = 0
                nodechar_filename = origin_filename.replace("ä", "ae")
                nodechar_filename = nodechar_filename.replace("Ä", "Ae")
                nodechar_filename = nodechar_filename.replace("ö", "oe")
                nodechar_filename = nodechar_filename.replace("Ö", "Oe")
                nodechar_filename = nodechar_filename.replace("ü", "ue")
                nodechar_filename = nodechar_filename.replace("Ü", "Ue")
                nodechar_filename = nodechar_filename.replace("ß", "ss")
                if nodechar_filename != origin_filename:
                    source_path = os.path.join(root, origin_filename)
                    target_path = os.path.join(root, nodechar_filename)
                    if os.path.exists(source_path):
                        os.rename(source_path, target_path)
                    else:
                        tocheck_lines.append(origin_filename)
                    print("Source: %s" % source_path)
                    print("Target: %s" % target_path)
                else:
                    source_path = os.path.join(root, origin_filename)
                    if not os.path.exists(source_path):
                        tocheck_lines.append(origin_filename)
                if b_break_nextfile == True:
                    break
            if b_break_nextfile == True:
                    break
        if b_break_nextfolder == True:
            break
    if len(tocheck_lines) != 0:
        print("Report: ")
        print("=" * 30)
        print("\n".join(tocheck_lines))



########################################
# FIX BRS：remove the german characters# 
########################################
def fix_filenames_in_brs(brs_fullpath=""):
    """[summary]

    Args:
        brs_fullpath (str, optional): [description]. Defaults to "".
    """
    backup_lines = []
    content_lines = []
    tocheck_lines = []
    with open(brs_fullpath, "r", encoding="utf-8") as brs:
        content_lines = brs.readlines()
    for lns in content_lines:
        if "|" in lns:
            origin_lns = lns.replace("\n", "") 
            lns_infos = origin_lns.split("| ")
            origin_filename = lns_infos[1]
            if "Linien_B" in origin_filename:
                a = 0
            nodechar_filename = origin_filename.replace("ä", "ae")
            nodechar_filename = nodechar_filename.replace("Ä", "Ae")
            nodechar_filename = nodechar_filename.replace("ö", "oe")
            nodechar_filename = nodechar_filename.replace("Ö", "Oe")
            nodechar_filename = nodechar_filename.replace("ü", "ue")
            nodechar_filename = nodechar_filename.replace("Ü", "Ue")
            nodechar_filename = nodechar_filename.replace("ß", "ss")
            if nodechar_filename != origin_filename:
                source_path = os.path.join(TEMPALTES_BASE_PATH, origin_filename)
                target_path = os.path.join(TEMPALTES_BASE_PATH, nodechar_filename)
                if os.path.exists(source_path):
                    os.rename(source_path, target_path)
                else:
                    tocheck_lines.append(origin_filename)
                lns = lns.replace(origin_filename, nodechar_filename)
                print("Source: %s" % source_path)
                print("Target: %s" % target_path)
            else:
                source_path = os.path.join(TEMPALTES_BASE_PATH, origin_filename)
                if not os.path.exists(source_path):
                    tocheck_lines.append(origin_filename)
        else:
            pass
        backup_lines.append(lns)
    print("Report: ")
    print("=" * 30)
    print("\n".join(tocheck_lines))
    with open(brs_fullpath, "w", encoding="utf-8") as brs:
        brs.writelines(backup_lines)
        

########################################
# FIX HHP：remove the german characters# 
########################################
def fix_filenames_in_hhp(hhp_fullpath=""):
    """[summary]

    Args:
        brs_fullpath (str, optional): [description]. Defaults to "".
    """
    backup_lines = []
    content_lines = []
    tocheck_lines = []
    with open(hhp_fullpath, 'r', encoding="utf-8") as hhp:
        bFindFiles = False
        lines = hhp.readlines()
        for lns in lines:
            if '[FILES]' in lns:
                backup_lines.append('[FILES]\n')
                bFindFiles = True
                continue
            if bFindFiles == False:
                backup_lines.append(lns)
                continue
            origin_lns = lns.replace("\n", "") 
            origin_filename = origin_lns
            if "Linien_B" in origin_filename:
                a = 0
            nodechar_filename = origin_filename.replace("ä", "ae")
            nodechar_filename = nodechar_filename.replace("Ä", "Ae")
            nodechar_filename = nodechar_filename.replace("ö", "oe")
            nodechar_filename = nodechar_filename.replace("Ö", "Oe")
            nodechar_filename = nodechar_filename.replace("ü", "ue")
            nodechar_filename = nodechar_filename.replace("Ü", "Ue")
            nodechar_filename = nodechar_filename.replace("ß", "ss")
            if nodechar_filename != origin_filename:
                source_path = os.path.join(TEMPALTES_BASE_PATH, origin_filename)
                target_path = os.path.join(TEMPALTES_BASE_PATH, nodechar_filename)
                if os.path.exists(source_path):
                    os.rename(source_path, target_path)
                else:
                    tocheck_lines.append(origin_filename)
                lns = lns.replace(origin_filename, nodechar_filename)
                print("Source: %s" % source_path)
                print("Target: %s" % target_path)
            else:
                source_path = os.path.join(TEMPALTES_BASE_PATH, origin_filename)
                if not os.path.exists(source_path):
                    tocheck_lines.append(origin_filename)
            backup_lines.append(lns)
    print("Report: ")
    print("=" * 30)
    print("\n".join(tocheck_lines))
    with open(hhp_fullpath, "w", encoding="utf-8") as brs:
        brs.writelines(backup_lines)
        

########################################
# FIX HHC：remove the german characters# 
########################################
def fix_filenames_in_hhc(hhc_fullpath=""):
    """[summary]

    Args:
        hhc_fullpath (str, optional): [description]. Defaults to "".
    """
    html_content = ''
    with open(hhc_fullpath, 'r', encoding="utf-8") as hhc:
        html_content = hhc.read()
    if html_content == '':
        return False
    
    def fix_name_local(input_string=''):
        nodechar = input_string.replace("ä", "ae")
        nodechar = nodechar.replace("Ä", "Ae")
        nodechar = nodechar.replace("ö", "oe")
        nodechar = nodechar.replace("Ö", "Oe")
        nodechar = nodechar.replace("ü", "ue")
        nodechar = nodechar.replace("Ü", "Ue")
        nodechar = nodechar.replace("ß", "ss")
        nodechar = nodechar.replace("&auml;", "ae")
        nodechar = nodechar.replace("&Auml;", "Ae")
        nodechar = nodechar.replace("&ouml;", "oe")
        nodechar = nodechar.replace("&Ouml;", "Oe")
        nodechar = nodechar.replace("&uuml;", "ue")
        nodechar = nodechar.replace("&Uuml;", "Ue")
        nodechar = nodechar.replace("&szlig;", "ss")
        return nodechar

    html_content = fix_name_local(html_content)
    with open(hhc_fullpath, "w", encoding="utf-8") as hhc:
        hhc.write(html_content)


########################################
# CHM：build project, clean project    # 
########################################
def translate_brs_and_export(str_sub_folder="", str_brs_template_name="", vCountryCode="044", encoding="utf-8"):
    """
    Test translate *.brs file
    
    >>> str_build_folder = "../Build Folder/"
    >>> vCountryCode = "044"
    >>> translate_brs_and_export(str_build_folder, vCountryCode)
    
    """
    try:
        brs_templates_path = os.path.join(CHM_EXTRA_BASE_PATH, str_sub_folder, str_brs_template_name)
        if PRINT_DEBUG:
            print("Try to get template: %s" % (brs_templates_path))
        ss = get_template(brs_templates_path).render()
        ss = ss.replace("\n\n", "\n")
        utf8_content = ss.replace(u'\ufeff\n', '', 1)
        strGoal = str_brs_template_name.replace("xxx", vCountryCode)
        strDest = os.path.join(CHM_BUILD_BASE_PATH, strGoal)
        # 编码为 GB2312
        gb2312_content = utf8_content.encode('gb2312', errors='ignore')
        if PRINT_DEBUG:
            print(gb2312_content)
        with open(strDest, 'wb') as file:
            file.write(gb2312_content)
        return True
    except Exception as e:
        if PRINT_DEBUG:
            print("Can not render the template: %s" % (brs_templates_path))
            print("Error details: %s" % e)
        return False


def translate_hhc_and_export(str_sub_folder="", str_hhc_template_name="", vCountryCode="044", encoding="utf-8"):
    """
    Test translate *.hhc file
    
    >>> str_build_folder = "../Build Folder/"
    >>> vCountryCode = "044"
    >>> translate_hhc_and_export(str_build_folder, vCountryCode)
    
    """
    try:
        hhc_templates_path = os.path.join(CHM_EXTRA_BASE_PATH, str_sub_folder, str_hhc_template_name)
        if PRINT_DEBUG:
            print("Try to get template: %s" % (hhc_templates_path))
        ss = get_template(hhc_templates_path).render()
        ss = ss.replace("\n\n", "\n")
        utf8_content = ss.replace(u'\ufeff\n', '', 1)
        strGoal = str_hhc_template_name.replace("xxx", vCountryCode)
        strDest = os.path.join(CHM_BUILD_BASE_PATH, strGoal)
        # 编码为 GB2312
        gb2312_content = utf8_content.encode('gb2312', errors='ignore')
        if PRINT_DEBUG:
            print(gb2312_content)
        with open(strDest, 'wb') as file:
            file.write(gb2312_content)
        return True
    except Exception as e:
        if PRINT_DEBUG:
            print("Can not render the template: %s" % (hhc_templates_path))
            print("Error details: %s" % e)
        return False


def translate_hhk_and_export(str_sub_folder="", str_hhk_template_name="", vCountryCode="044", encoding="utf-8"):
    """
    Test translate *.hhk file
    
    >>> str_build_folder = "../build/"
    >>> vCountryCode = "044"
    >>> translate_hhk_and_export(str_build_folder, vCountryCode)
    
    """
    try:
        hhk_templates_path = os.path.join(CHM_EXTRA_BASE_PATH, str_sub_folder, str_hhk_template_name)
        if PRINT_DEBUG:
            print("Try to get template: %s" % (hhk_templates_path))
        ss = get_template(hhk_templates_path).render()
        ss = ss.replace("\n\n", "\n")
        utf8_content = ss.replace(u'\ufeff\n', '', 1)
        strGoal = str_hhk_template_name.replace("xxx", vCountryCode)
        strDest = os.path.join(CHM_BUILD_BASE_PATH, strGoal)
        # 编码为 GB2312
        gb2312_content = utf8_content.encode('gb2312', errors='ignore')
        if PRINT_DEBUG:
            print(gb2312_content)
        with open(strDest, 'wb') as file:
            file.write(gb2312_content)
        return True
    except Exception as e:
        if PRINT_DEBUG:
            print("Can not render the template: %s" % (hhk_templates_path))
            print("Error details: %s" % e)
        return False


def translate_hhp_and_export(str_sub_folder="", str_hhp_template_name="", vCountryCode="044", encoding="utf-8"):
    """
    Test translate *.hhp file
    
    >>> str_build_folder = "../build/"
    >>> vCountryCode = "044"
    >>> translate_hhp_and_export(str_build_folder, vCountryCode)
    
    """
    try:
        hhp_templates_path = os.path.join(CHM_EXTRA_BASE_PATH, str_sub_folder, str_hhp_template_name)
        if PRINT_DEBUG:
            print("Try to get template: %s" % (hhp_templates_path))
        ss = get_template(hhp_templates_path).render()
        ss = ss.replace("\n\n", "\n")
        utf8_content = ss.replace(u'\ufeff\n', '', 1)
        strGoal = str_hhp_template_name.replace("xxx", vCountryCode)
        strDest = os.path.join(CHM_BUILD_BASE_PATH, strGoal)
        # 编码为 GB2312
        gb2312_content = utf8_content.encode('gb2312', errors='ignore')
        if PRINT_DEBUG:
            print(gb2312_content)
        with open(strDest, 'wb') as file:
            file.write(gb2312_content)
        return True
    except Exception as e:
        if PRINT_DEBUG:
            print("Can not render the template: %s" % (hhp_templates_path))
            print("Error details: %s" % e)
        return False


def translate_glo_and_export(str_sub_folder="", str_glo_template_name="", vCountryCode="044", encoding="utf-8"):
    """
    Test translate *.glo file
    
    >>> str_build_folder = "../build/"
    >>> vCountryCode = "044"
    >>> translate_glo_and_export(str_build_folder, vCountryCode)
    
    """
    try:
        glo_templates_path = os.path.join(CHM_EXTRA_BASE_PATH, str_sub_folder, str_glo_template_name)
        if PRINT_DEBUG:
            print("Try to get template: %s" % (glo_templates_path))
        ss = get_template(glo_templates_path).render()
        ss = ss.replace("\n\n", "\n")
        cont = ss.replace(u'\ufeff\n', '', 1)
        strGoal = str_glo_template_name.replace("xxx", vCountryCode)
        strDest = os.path.join(CHM_BUILD_BASE_PATH, strGoal)
        fw= codecs.open(strDest, "w", encoding)
        if PRINT_DEBUG:
            print(cont)
        fw.write(cont)
        fw.close()
        return True
    except Exception as e:
        if PRINT_DEBUG:
            print("Can not render the template: %s" % (glo_templates_path))
            print("Error details: %s" % e)
        return False


def translate_lng_and_export(str_sub_folder="", str_lng_template_name="", vCountryCode="044", encoding="utf-8"):
    """
    Test translate *.lng file
    
    >>> str_build_folder = "../build/"
    >>> vCountryCode = "044"
    >>> translate_lng_and_export(str_build_folder, vCountryCode)
    
    """
    try:
        lng_templates_path = os.path.join(CHM_EXTRA_BASE_PATH, str_sub_folder, str_lng_template_name)
        if PRINT_DEBUG:
            print("Try to get template: %s" % (lng_templates_path))
        ss = get_template(lng_templates_path).render()
        ss = ss.replace("\n\n", "\n")
        cont = ss.replace(u'\ufeff\n', '', 1)
        strGoal = str_lng_template_name.replace("xxx", vCountryCode)
        strDest = os.path.join(CHM_BUILD_BASE_PATH, strGoal)
        fw= codecs.open(strDest, "w", encoding)
        if PRINT_DEBUG:
            print(cont)
        fw.write(cont)
        fw.close()
        return True
    except Exception as e:
        if PRINT_DEBUG:
            print("Can not render the template: %s" % (lng_templates_path))
            print("Error details: %s" % e)
        return False


def translate_templates_and_export(str_sub_folder_name="", str_template_name="", encoding="utf-8"):
    """
    Test translate *.htm file of "templates" folder
    
    >>> str_sub_folder_name = "Common"
    >>> str_template_name = "Abbrechen_Common.htm"
    >>> str_build_folder = "../build/"
    >>> translate_templates_and_export(str_sub_folder_name, str_template_name)
    
    """
    strTempPath = os.path.join(TEMPALTES_BASE_PATH, str_sub_folder_name, str_template_name)
    try:
        if PRINT_DEBUG:
            print("Try to get template from path: %s" % strTempPath)
        ss = get_template(strTempPath).render({'encoding':encoding })
        ss = ss.replace("\n\n", "\n")
        cont = ss.replace(u'\ufeff\n', '', 1)
        cont = cont.replace(u'\xa0', ' ')
        strDestPath = os.path.join(CHM_BUILD_BASE_PATH, str_sub_folder_name, str_template_name)
        if not os.path.exists(os.path.join(CHM_BUILD_BASE_PATH, str_sub_folder_name)):
            os.mkdir(os.path.join(CHM_BUILD_BASE_PATH, str_sub_folder_name))
        if PRINT_DEBUG:
            print("Got template, save the rendered template into path: %s" % strDestPath)
        fw= codecs.open(strDestPath, "w", encoding)
        #if PRINT_DEBUG:
        #    print(cont)
        fw.write(cont)
        fw.close()
        return
    except Exception as e:
        if PRINT_DEBUG:
            print("Can not render the template: %s" % strTempPath)
            print("Error details: %s" % e)
        return (strTempPath, e)


def get_list_of_templates_relative_path(str_template_base="", tuple_extension=('.htm')):
    """
    Get all htm templaste with subfoler name
    return list of tuples, (sub, name)
    
    >>> str_template_base = os.path.join(settings.BASE_DIR, "templates")
    >>> DoGetListOfTemplates(str_template_base)
    
    """
    if PRINT_DEBUG:
            print("Try to get the templates in type *.htm")
    listFiles = []
    for strFilePath, dummy_dirs, ltFiles in os.walk(str_template_base):
        if strFilePath == str_template_base:
            subfoler = ""
        else:
            dummy_rest, subfoler = os.path.split(strFilePath)
        for strFile in ltFiles:
            # pre-filter
            if not strFile.endswith(tuple_extension):
                continue
            else:
                pass
            
            listFiles.append((subfoler, strFile))
    if PRINT_DEBUG:
            print("Got the templates in type *.htm")
    return listFiles


def clean_build_folder():
    """
    delete & clean the build folder
    """
    try:
        if PRINT_DEBUG:
            print("Try to clean the build folder")
        for strFilePath, dummy_dirs, ltFiles in os.walk(CHM_BUILD_BASE_PATH):
            for strFile in ltFiles:
                file_path = os.path.join(strFilePath, strFile)
                if os.path.isfile(file_path):
                    os.unlink(file_path)
                #elif os.path.isdir(file_path): shutil.rmtree(file_path)
        if PRINT_DEBUG:
            print("Done, clean the build folder")
        return True
    except Exception as e:
        if PRINT_DEBUG:
            print("Can not clean the build folder")
            print("Error details: %s" % e)
        return False

def export_static_and_export(str_static_base="", str_sub_path="", tuple_extension=('.css', '.js', 'jpg', '.gif')):
    """
    export the necessary javascript/css/image file and export to build folder
    """
    try:
        str_full_base = os.path.join(str_static_base, str_sub_path)
        if PRINT_DEBUG:
                print("Try to export the static from: %s" % (str_full_base))
                print("Try to export the static in type %s" % (str(tuple_extension)))
        for strFilePath, dummy_dirs, ltFiles in os.walk(str_full_base):
            if strFilePath == str_full_base:
                subfoler = ""
            else:
                if not CHM_CHECK_STATIC_SUBFOLDER:
                    break
                dummy_rest, subfoler = os.path.split(strFilePath)
            for strFile in ltFiles:
                # pre-filter
                if not strFile.endswith(tuple_extension):
                    continue
                else:
                    pass
                source_path = os.path.join(str_full_base, subfoler, strFile)
                if PRINT_DEBUG:
                    print("Exporting the static file from: %s" % (source_path))
                destin_path = os.path.join(CHM_BUILD_BASE_PATH, subfoler, strFile)
                if PRINT_DEBUG:
                    print("Exporting the static file to: %s" % (destin_path))
                if not os.path.exists(os.path.join(CHM_BUILD_BASE_PATH, subfoler)):
                    os.mkdir(os.path.join(CHM_BUILD_BASE_PATH, subfoler));
                shutil.copy(source_path, destin_path)
        if PRINT_DEBUG:
                print("Got the static file in type *.htm")
        return True
    except Exception as e:
        if PRINT_DEBUG:
            print("Can not export the static files to the build folder")
            print("Error details: %s" % e)
        return False


########################################
# Main functions                       # 
########################################
def main(args):
    """[summary]

    Args:
        args ([type]): [description]
    """
    #[collect], collect the origin htm/hhp/hhk/js etc. files from origin to templates/static
    if 'collect' in args:
        if len(args) == 2 and 'htm' in args:
            collect_htm_files()
        elif len(args) == 3 and 'static' in args and 'all' in args:
            collect_all_static_files()
        elif len(args) == 3 and 'static' in args and 'js' in args:
            collect_js_static_files()
        else:
            print("python executor.py collect static all")
            print("python executor.py collect static js")
            print("python executor.py collect htm ")
        return 

    #[convert], convert the htm files to templates
    elif 'convert' in args:
        if len(args) == 3 and 'step' in args:
            convert_htm_to_template(str_relativ_path=args[2], b_break_nextfile=True)
        elif len(args) == 3 and 'folder' in args:
            convert_htm_to_template(str_relativ_path=args[2], b_break_nextfile=False, b_break_nextfolder=True)
        elif len(args) == 3 and 'full' in args:
            convert_htm_to_template(str_relativ_path=args[2], b_break_nextfile=False, b_break_nextfolder=False)
        else:
            print("python executor.py convert step <relative path (subfolder) of template folder>")
            print("python executor.py convert folder <relative path (subfolder) of template folder>")
            print("python executor.py convert full <relative path (subfolder) of template folder>")
        return 

    #[transcode], Transcode save the htm template, default is from cp1252 to utf-8, or specify the source encoding and the target encoding.
    if 'transcode' in args:
        if len(args) == 3 and 'file' in args:
            transcode_file(b_folder_or_file=False, str_relativ_path=args[2])
        elif len(args) == 3 and 'step' in args:
            transcode_file(b_folder_or_file=True, str_relativ_path=args[2], b_break_nextfile=True)
        elif len(args) == 3 and 'folder' in args:
            transcode_file(b_folder_or_file=True, str_relativ_path=args[2], b_break_nextfile=False, b_break_nextfolder=True)
        elif len(args) == 3 and 'full' in args:
            transcode_file(b_folder_or_file=True, str_relativ_path=args[2], b_break_nextfile=False, b_break_nextfolder=False)
        else:
            print("python executor.py transcode file <relative path with filename of template folder>")
            print("python executor.py transcode step <relative path (subfolder) of template folder>")
            print("python executor.py transcode folder <relative path (subfolder) of template folder>")
            print("python executor.py transcode full <relative path (subfolder) of template folder>")
        return 

    #[fix], fix brs, check if there is german character in the filename, if yes then fix it and rename the htm files
    elif 'fix' in args:
        if len(args) == 2 and "brs" in args:
            brs_file_path = os.path.join(CHM_EXTRA_BASE_PATH, "086\\wire_xxx.brs")
            fix_filenames_in_brs(brs_fullpath=brs_file_path)
        elif len(args) == 3 and "brs" in args:
            brs_file_path = args[2]
            fix_filenames_in_brs(brs_fullpath=brs_file_path)
        if len(args) == 2 and "hhp" in args:
            hhp_file_path = os.path.join(CHM_EXTRA_BASE_PATH, "086\\wire_xxx.hhp")
            fix_filenames_in_hhp(hhp_fullpath=hhp_file_path)
        elif len(args) == 3 and "hhp" in args:
            hhp_file_path = args[2]
            fix_filenames_in_hhp(hhp_fullpath=hhp_file_path)
        if len(args) == 2 and "hhc" in args:
            hhc_file_path = os.path.join(CHM_EXTRA_BASE_PATH, "086\\wire_xxx.hhc")
            fix_filenames_in_hhc(hhc_fullpath=hhc_file_path)
        elif len(args) == 3 and "hhc" in args:
            hhc_file_path = args[2]
            fix_filenames_in_hhc(hhc_fullpath=hhc_file_path)
        else:
            print("python executor.py fix hhp")
            print("python executor.py fix hhp <hhp relative path of source folder>")
            print("python executor.py fix brs")
            print("python executor.py fix brs <brs relative path of source folder>")
        return 

    #[fixname], fix the name of template fiels, check if there is german character in the href, if yes then remove it
    elif 'fixname' in args:
        if len(args) == 3 and 'step' in args:
            fix_filename_of_template(str_relativ_path=args[2], b_break_nextfile=True)
        elif len(args) == 3 and 'folder' in args:
            fix_filename_of_template(str_relativ_path=args[2], b_break_nextfile=False, b_break_nextfolder=True)
        elif len(args) == 3 and 'full' in args:
            fix_filename_of_template(str_relativ_path=args[2], b_break_nextfile=False, b_break_nextfolder=False)
        else:
            print("python executor.py fixname step <relative path (subfolder) of template folder>")
            print("python executor.py fixname folder <relative path (subfolder) of template folder>")
            print("python executor.py fixname full <relative path (subfolder) of template folder>")
        return 

    #[fixinnerhref], fix innerhref of template fiels, check if there is german character in the href, if yes then remove it
    elif 'fixinnerhref' in args:
        if len(args) == 3 and 'file' in args:
            fix_innerhref_in_template(b_folder_or_file=False, str_relativ_path=args[2])
        elif len(args) == 3 and 'step' in args:
            fix_innerhref_in_template(b_folder_or_file=True, str_relativ_path=args[2], b_break_nextfile=True)
        elif len(args) == 3 and 'folder' in args:
            fix_innerhref_in_template(b_folder_or_file=True, str_relativ_path=args[2], b_break_nextfile=False, b_break_nextfolder=True)
        elif len(args) == 3 and 'full' in args:
            fix_innerhref_in_template(b_folder_or_file=True, str_relativ_path=args[2], b_break_nextfile=False, b_break_nextfolder=False)
        else:
            print("python executor.py fixinnerhref file <relative path with filename of template folder>")
            print("python executor.py fixinnerhref step <relative path (subfolder) of template folder>")
            print("python executor.py fixinnerhref folder <relative path (subfolder) of template folder>")
            print("python executor.py fixinnerhref full <relative path (subfolder) of template folder>")
        return 

    #[launch], launch a selenium weberdirver, save the info into .selenium-dirver-info in local folder
    elif 'launch' in args:
        print("Executor would launch an selenium web driver.")
        if len(args) == 2 and "chrome" in args:
            driver_infos = {"port": None, "session_id": None}
            options = webdriver.ChromeOptions()
            #options.add_argument("headless")
            driver = webdriver.Chrome(executable_path=SELENIUM_DRIVER_LOCATION, options=options)
            driver_infos['port'] = driver.command_executor._url.split(':')[2]
            print(driver.command_executor._url)
            driver_infos['session_id'] = driver.session_id
            print(driver.session_id)
            with open(os.path.join(".", ".selenium-dirver-info"), 'wt') as df:
                data = str(driver_infos)
                df.write(data)
            print("The selenium driver info will be stored in file .selenium-dirver-info, in current folder")
            def end_process(signum, frame):
                print('Terminate the current process.')
                sys.exit()
            signal.signal(signal.SIGINT, end_process)
            signal.signal(signal.SIGTERM, end_process)
            while True:
                pass
        elif len(args) == 3 and "chrome" in args:
            driver_infos = {"port": None, "session_id": None}
            options = webdriver.ChromeOptions()
            #options.add_argument("headless")
            driver = webdriver.Chrome(executable_path=args[2], options=options)
            driver_infos['port'] = driver.command_executor._url.split(':')[2]
            print(driver.command_executor._url)
            driver_infos['session_id'] = driver.session_id
            print(driver.session_id)
            print("The selenium driver info will be stored in file .selenium-dirver-info, in current folder")
            def end_process(signum, frame):
                print('Terminate the current process.')
                sys.exit()
            signal.signal(signal.SIGINT, end_process)
            signal.signal(signal.SIGTERM, end_process)
            while True:
                pass
        else:
            print("python executor.py launch chrome")
            print("python executor.py launch chrome <selenium driver path>")
        return 
    
    #viewer a template file in the selenium weberdirver
    elif 'viewer' in args:
        print("Executor would viewer a template file.")
        if len(args) == 2:
            driver_infos = None
            if os.path.exists(os.path.join(".", ".selenium-dirver-info")):
                with open(os.path.join(".", ".selenium-dirver-info"), 'r') as df:
                    data = df.read()
                    driver_infos = eval(data)
            if driver_infos != None:
                option = webdriver.ChromeOptions()
                option.add_argument('headless')
                executor_url = 'http://127.0.0.1:%s' % driver_infos['port']
                try:
                    driver = webdriver.Remote(command_executor=executor_url, desired_capabilities={}, options=option)
                    driver.close()   # this prevents the dummy browser
                    driver.session_id = driver_infos['session_id']
                    ### open in webbrower driver
                    js = "window.open('http://127.0.0.1:8000/%s')" % (args[1])
                    driver.execute_script(js)
                    print("Viewer has open the template in the selenium driver: %s" % executor_url)
                except:
                    print("Check whether the chrome selenium driver is running")
        else:
            print("python executor.py viewer <template file's relative path>")
        return 
    
    #[clean] the build path
    elif 'clean' in args:
        print("Executor would clean the build folder.")
        clean_build_folder()
    
    #[export] all static files such as *.jpg, *.css, *.js file, export to build folder
    elif 'export_static' in args:
        print("Executor would export all static files into the build folder.")
        export_static_and_export(CHM_STATC_BASE_PATH, "")
        return 

    #[render] htm, brs, hhc, hhk, hhp, lng file or all files (from templates to htm/html file)
    elif 'render' in args:
        print("Executor would render the template file into build folder.")
        translation.activate(settings.LANGUAGE_CODE)
        contry_code = CHM_TRANSLATE_CONTRY_CODES[settings.LANGUAGE_CODE]
        asset_sub_folder = contry_code
        encoding_code = CHM_FILES_CODING_LIST[contry_code]
        if len(args) >= 2:
            if "htm" in args and len(args) == 2:
                if PRINT_DEBUG:
                    print("Render the %s templates!" % ("htm"))
                list_templates = get_list_of_templates_relative_path(TEMPALTES_BASE_PATH, ('.htm'))
                export_results = []
                for relative_path, file_name in list_templates:
                    if PRINT_DEBUG:
                        print("Render the template %s\\%s", (relative_path, file_name))
                    rts = translate_templates_and_export(relative_path, file_name, encoding_code)
                    if rts != None:
                        export_results.append(rts)
                if PRINT_DEBUG == True and len(export_results) != 0:
                    for result in export_results:
                        print("--" * 20)
                        print("Error details: %s" % result[0])
                        print("Error details: %s" % result[1])
            if "htm" in args and len(args) > 2:
                if PRINT_DEBUG:
                    print("Render the %s templates (single file case)!" % ("htm"))
                relative_path, file_name = os.path.split(args[2])
                if PRINT_DEBUG:
                    print("Render the template %s\\%s", (relative_path, file_name))
                rts = translate_templates_and_export(relative_path, file_name, encoding_code)
                if PRINT_DEBUG == True and rts != None:
                    print("--" * 20)
                    print("Error details: %s" % rts[0])
                    print("Error details: %s" % rts[1])
            elif "hhk" in args:
                if PRINT_DEBUG:
                    print("Render the %s templates!" % ("hhk"))
                translate_hhk_and_export(asset_sub_folder, CHM_HHK_TEMPLATE, contry_code, encoding_code)
            elif "hhc" in args:
                if PRINT_DEBUG:
                    print("Render the %s templates!" % ("hhc"))
                translate_hhc_and_export(asset_sub_folder, CHM_HHC_TEMPLATE, contry_code, encoding_code)
            elif "hhp" in args:
                if PRINT_DEBUG:
                    print("Render the %s templates!" % ("hhp"))
                translate_hhp_and_export(asset_sub_folder, CHM_HHP_TEMPLATE, contry_code, encoding_code)
            elif "brs" in args:
                if PRINT_DEBUG:
                    print("Render the %s templates!" % ("brs"))
                translate_brs_and_export(asset_sub_folder, CHM_BRS_TEMPLATE, contry_code, encoding_code)
            elif "lng" in args:
                if PRINT_DEBUG:
                    print("Render the %s templates!" % ("lng"))
                translate_lng_and_export(asset_sub_folder, CHM_LNG_TEMPLATE, contry_code, encoding_code)
            else:
                print("python executor.py build [lng/hhc/hhp/hhk/brs/htm]")
        elif len(args) == 1:
            if PRINT_DEBUG:
                print("Render the %s templates!" % ("htm"))
            list_templates = get_list_of_templates_relative_path(TEMPALTES_BASE_PATH, ('.htm'))
            export_results = []
            for relative_path, file_name in list_templates:
                if PRINT_DEBUG:
                    print("Render the template %s\\%s", (relative_path, file_name))
                rts = translate_templates_and_export(relative_path, file_name, encoding_code)
                if rts != None:
                    export_results.append(rts)
            if PRINT_DEBUG == True and len(export_results) != 0:
                for result in export_results:
                    print("--" * 20)
                    print("Error details: %s" % result[0])
                    print("Error details: %s" % result[1])
            if PRINT_DEBUG:
                print("Render the %s templates!" % ("lng"))
            translate_lng_and_export(asset_sub_folder, CHM_LNG_TEMPLATE, contry_code, encoding_code)
            if PRINT_DEBUG:
                print("Render the %s templates!" % ("hhk"))
            translate_hhk_and_export(asset_sub_folder, CHM_HHK_TEMPLATE, contry_code, encoding_code)
            if PRINT_DEBUG:
                print("Render the %s templates!" % ("hhc"))
            translate_hhc_and_export(asset_sub_folder, CHM_HHC_TEMPLATE, contry_code, encoding_code)
            if PRINT_DEBUG:
                print("Render the %s templates!" % ("hhp"))
            translate_hhp_and_export(asset_sub_folder, CHM_HHP_TEMPLATE, contry_code, encoding_code)
            if PRINT_DEBUG:
                print("Render the %s templates!" % ("brs"))
            translate_brs_and_export(asset_sub_folder, CHM_BRS_TEMPLATE, contry_code, encoding_code)
        else:
            print("python executor.py render")
            print("python executor.py render [lng/hhc/hhp/hhk/brs/htm]")
        translation.deactivate()
        return 
    else:
        print("python executor.py export_static")
        print("python executor.py clean")
        print("python executor.py collect static all")
        print("python executor.py collect static js")
        print("python executor.py collect htm ")
        print("python executor.py transcode file <relative path with filename of template folder>")
        print("python executor.py transcode step <relative path (subfolder) of template folder>")
        print("python executor.py transcode folder <relative path (subfolder) of template folder>")
        print("python executor.py transcode full <relative path (subfolder) of template folder>")
        print("python executor.py fix hhp")
        print("python executor.py fix hhp <hhp relative path of source folder>")
        print("python executor.py fix brs")
        print("python executor.py fix brs <brs file's relative path of source folder>")
        print("python executor.py fix hhc")
        print("python executor.py fix hhc <hhp relative path of source folder>")
        print("python executor.py fixname step <relative path (subfolder) of template folder>")
        print("python executor.py fixname folder <relative path (subfolder) of template folder>")
        print("python executor.py fixname full <relative path (subfolder) of template folder>")
        print("python executor.py fixinnerhref file <relative path with filename of template folder>")
        print("python executor.py fixinnerhref step <relative path (subfolder) of template folder>")
        print("python executor.py fixinnerhref folder <relative path (subfolder) of template folder>")
        print("python executor.py fixinnerhref full <relative path (subfolder) of template folder>")
        print("python executor.py convert step <relative path (subfolder) of template folder>")
        print("python executor.py convert folder <relative path (subfolder) of template folder>")
        print("python executor.py convert full <relative path (subfolder) of template folder>")
        print("python executor.py launch chrome")
        print("python executor.py launch chrome <selenium driver path>")
        print("python executor.py render xxxx")
        print("python executor.py render [lng/hhc/hhp/hhk/brs/htm]")
        print("python executor.py viewer <htm template relative path>")
    return 

if __name__ == '__main__':
    main(sys.argv[1:])