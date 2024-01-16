import os
import re
import time
from hashlib import md5
from selenium import webdriver
from selenium.webdriver.chrome.service import Service as ChromeService
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from bs4 import BeautifulSoup
import pygetwindow as gw
import pyautogui

try:
    from myapp import settings  # @UnusedImport
except:
    pass

"""
本py模块将 template模版，通过selenium结合chrome中的google自动翻译origin中的html，将翻译后的body保存到相应的模版文件中。 
在此过程中通过检测模版文件是否有trans标识来确定模版是否完成翻译。
"""

def checkout_template_translation(template_path=""):
    if not os.path.exists(template_path):
        return False
    with open(template_path, "r", encoding="utf-8") as tm:
        lines_file = tm.readlines()
    fond_start = False
    for ln in lines_file:
        if 'block mainbody' in ln:
            fond_start = True
            continue
        if 'endblock' in ln and fond_start == True:
            break
        elif "% trans" in ln and fond_start == True:
            return True
        else:
            pass
    return False

def generate_messages_records(message_path=""):
    """massage_path, po file

    message_file = os.path.join(settings.BASE_DIR, "locale", 'zh_hans', "LC_MESSAGES", "django.po")
    Args:
        message_path (str, optional): _description_. Defaults to "".

    Returns:
        _type_: _description_
    """
    if not os.path.exists(message_path):
        return False
    with open(message_path, "r", encoding="utf-8") as tm:
        lines_file = tm.readlines()
    msgid = ""
    records = []
    for ln in lines_file:
        if 'msgid' in ln:
            fixln = ln.replace('\n', '')
            fixln = fixln.replace('msgid ', '')
            fixln = fixln.lstrip('"')
            fixln = fixln.rstrip('"')
            if fixln == '""':
                msgid = ""
                continue
            msgid = fixln
        elif 'msgstr' in ln and msgid != "":
            fixln = ln.replace('\n', '')
            fixln = fixln.replace('msgstr ', '')
            fixln = fixln.lstrip('"')
            fixln = fixln.rstrip('"')
            msgstr = fixln
            md5_value = md5(msgid.encode('utf-8')).hexdigest()
            md5l16 = md5_value[:16]  # 取前16位
            records.append((md5l16, msgid, msgstr))
            msgid = ""
        else:
            pass
    with open("messages.records", "w", encoding='utf-8') as mr:
        for sR in records:
            mr.write(str(sR) + '\n')
    return True

def update_messages_pofile(message_path="", records_path=""):
    """ massage_path, po file
        records_path, messages.records file

    message_file = os.path.join(settings.BASE_DIR, "locale", 'zh_hans', "LC_MESSAGES", "django.po")
    Args:
        message_path (str, optional): _description_. Defaults to "".
        records_path (str, optional): _description_. Defaults to "".
    Returns:
        _type_: _description_
    """
    if not os.path.exists(message_path):
        return False
    if not os.path.exists(records_path):
        return False
    origin_records = []
    with open(records_path, 'r', encoding='utf-8') as mr:
        origin_records = mr.readlines()
    if len(origin_records) == 0:
        return False
    updated_messages = {}
    pattern = re.compile(r'[\u4e00-\u9fa5]')
    for ln in origin_records:
        fix_line = ln.rstrip('\n')
        tuple_record = eval(fix_line)
        if len(tuple_record) != 3:
            continue
        translated_id = tuple_record[0]
        translated_msg = tuple_record[2]
        if translated_msg != '' and bool(pattern.search(translated_msg)) == True:
            updated_messages[translated_id] = translated_msg
    if not updated_messages:
        return False
    with open(message_path, "r", encoding="utf-8") as tm:
        lines_file = tm.readlines()
    msgid = ""
    update_lines = []
    for ln in lines_file:
        if 'msgid' in ln:
            fixln = ln.replace('\n', '')
            fixln = fixln.replace('msgid ', '')
            fixln = fixln.lstrip('"')
            fixln = fixln.rstrip('"')
            if fixln == '""':
                msgid = ""
                continue
            msgid = fixln
            update_lines.append(ln)
        elif 'msgstr' in ln and msgid != "":
            fixln = ln.replace('\n', '')
            fixln = fixln.replace('msgstr ', '')
            fixln = fixln.lstrip('"')
            fixln = fixln.rstrip('"')
            msgstr = fixln
            md5_value = md5(msgid.encode('utf-8')).hexdigest()
            md5l16 = md5_value[:16]  # 取前16位
            if md5l16 in updated_messages:
                translated_message = updated_messages[md5l16]
                new_line = f'msgstr "{translated_message}"\n'
                update_lines.append(new_line)
            else:
                update_lines.append(ln)
        else:
            update_lines.append(ln)
    with open(message_path, "w", encoding='utf-8') as mr:
        mr.writelines(update_lines)
    return True


def translate_messages_records(msgrecords_path=""):
    """完成po文件的翻译，从po文件得到要翻译的字符列表，
    使用函数checkout_template_translation检查文件中body是否有% trans，确定该文件是否翻译。如果未翻译，则使用selenium加chrome打开，
    文件。

    Returns:
        _type_: _description_
    """
    if os.path.exists(msgrecords_path) == False:
        return False
    
    driver_infos = {"port": None, "session_id": None}
    chrome_options = Options()
    #options.add_argument("headless")
    chrome_options.add_argument("--lang=zh-Hans")  # 将 "en-US" 替换为您想要的语言代码
    # 添加选项，启用自动打开开发者工具
    # chrome_options.add_argument("--auto-open-devtools-for-tabs")
    chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
    chrome_options.add_experimental_option("useAutomationExtension", False)

    # 获取Templates文件列表
    TEMPALTES_BASE_PATH = os.path.join(settings.BASE_DIR, "templates")
    message_template = os.path.join(TEMPALTES_BASE_PATH, "messages.html")
    
    if os.path.exists(message_template) == False:
        return False
    
    # 启动 Chrome 浏览器
    chrome_service = ChromeService(executable_path="D:\\Eclipse-Works\\workspace\\PEPSWireDocGenerator\\extra\\chromedriver.exe")
    driver = webdriver.Chrome(service=chrome_service, options=chrome_options)
    # 最大化窗口（全屏）
    # driver.maximize_window()
    driver_infos['port'] = driver.command_executor._url.split(':')[2]
    print("# 驱动URL：" + driver.command_executor._url)
    # 获取当前窗口的 session id
    current_session_id = driver.session_id
    driver_infos['session_id'] = current_session_id
    print("# 驱动Session：" + current_session_id)
    
    chrome_windows = None
    # 获取所有打开的窗口
    for window in gw.getWindowsWithTitle("Google Chrome"):
        # 切换到当前窗口
        try:
            window.activate()
        except gw.PyGetWindowException:
            pass
        # 获取当前窗口的 session id
        current_window_session_id = driver.session_id
        # 如果 session id 匹配，将窗口添加到列表
        if current_window_session_id == current_session_id:
            chrome_windows = window
            break
        
    # 获取所有打开的窗口
    vscode_windows = None
    windows = gw.getWindowsWithTitle("Visual Studio Code")
    vscode_windows = windows[0]
    
    i_offset = 50
    is_continue = True
    is_reload = False
    soup = None
    while is_continue:
        url_full = f"http://127.0.0.1:8000/messages.html?id={i_offset}"
        try:
            rts = driver.get(url_full)
            # 获取页面源代码
            page_source = driver.page_source
            # 使用 BeautifulSoup 解析页面源代码
            soup = BeautifulSoup(page_source, 'html.parser')
            #
            body_content = soup.body
            size_p = soup.body.find_all('p')
            #
            if body_content.text == '404':
                print("# 无页面内容，代码404 退出。")
                break
            elif len(size_p) == 0:
                print("# 无页面内容，<p>长度0 退出。")
                break
            else:
                pass
        except:
            input(">>> 程序错误，任意键退出")
            #
            break
        time.sleep(1)
        actions = ActionChains(driver)
        # 等待页面中的某个元素出现，例如，这里等待一个 id 为 "myElement" 的元素
        time.sleep(1)
        # 鼠标右键菜单
        # 如果找到 Chrome 窗口，则激活它
        if chrome_windows:
            try:
                chrome_windows.activate()
            except gw.PyGetWindowException:
                pass
        actions.context_click().perform()
        time.sleep(1)
        pyautogui.typewrite(['up', 'up', 'up'])
        pyautogui.typewrite(['return'])
        time.sleep(8)
        #
        print("# 执行操作 continue, 完成翻译执行操作，获取翻译的页面内容。")
        # 获取页面源代码
        page_source = driver.page_source
        # 使用 BeautifulSoup 解析页面源代码
        soup = BeautifulSoup(page_source, 'html.parser')
        # 找到要删除的 div，假设要删除 id 为 "div2" 的 div
        div_to_remove = soup.find('div', {'id': 'goog-gt-tt'})
        if div_to_remove:
            div_to_remove.decompose()
        # 打印 <body> 内容
        # 提取页面的 <body> 内容
        body_content = soup.body
        # 
        list_p = body_content.find_all('p')
        translated_records = {}
        pattern = re.compile(r'[\u4e00-\u9fa5]')
        for p_node in list_p:
            node_id = p_node.get('id', '')
            node_message = p_node.text
            if node_id != '' and node_message != '' and bool(pattern.search(node_message)) == True:
                translated_records[node_id] = node_message
        if translated_records:
            origin_records = []
            tosave_records = []
            b_records_updated = False
            with open(msgrecords_path, 'r', encoding='utf-8') as mr:
                origin_records = mr.readlines()
            if len(origin_records) == 0:
                pass
            try:
                for ln in origin_records:
                    fix_line = ln.rstrip('\n')
                    list_record = list(eval(fix_line))
                    if len(list_record) != 3:
                        continue
                    msg_id = list_record[0]
                    if msg_id in translated_records:
                        list_record[2] = translated_records[msg_id]
                    tosave_records.append(tuple(list_record))
                b_records_updated = True
            except Exception as e:
                pass
            if b_records_updated:
                with open(msgrecords_path, "w", encoding='utf-8') as mr:
                    for sR in tosave_records:
                        mr.write(str(sR) + '\n')
        time.sleep(5)
    
    # 关闭浏览器
    driver.quit()

    
        
def translate_templates_files():
    """完成htm文件的翻译，从origin文件得到文件列表，在从templates找到对应的htm文件，
    使用函数checkout_template_translation检查文件中body是否有% trans，确定该文件是否翻译。如果未翻译，则使用selenium加chrome打开，
    文件。

    Returns:
        _type_: _description_
    """
    driver_infos = {"port": None, "session_id": None}
    chrome_options = Options()
    #options.add_argument("headless")
    chrome_options.add_argument("--lang=zh-Hans")  # 将 "en-US" 替换为您想要的语言代码
    # 添加选项，启用自动打开开发者工具
    # chrome_options.add_argument("--auto-open-devtools-for-tabs")
    chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
    chrome_options.add_experimental_option("useAutomationExtension", False)

    # 获取Templates文件列表
    list_templates = []
    ORIGIN_BASE_PATH = settings.BASE_DIR.replace("source", "origin")
    TEMPALTES_BASE_PATH = os.path.join(settings.BASE_DIR, "templates")
    for root, dirs, files in os.walk(os.path.join(TEMPALTES_BASE_PATH), topdown=False):
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
                relevant_base = re.sub(re.escape(TEMPALTES_BASE_PATH), '', root)
                new_record = os.path.join(relevant_base, single_file)
                list_templates.append(new_record)
    
    length_templates = len(list_templates)
    if length_templates == 0:
        return False
    
    # 启动 Chrome 浏览器
    chrome_service = ChromeService(executable_path="D:\\Eclipse-Works\\workspace\\PEPSWireDocGenerator\\extra\\chromedriver.exe")
    driver = webdriver.Chrome(service=chrome_service, options=chrome_options)
    # 最大化窗口（全屏）
    driver.maximize_window()
    driver_infos['port'] = driver.command_executor._url.split(':')[2]
    print("# 驱动URL：" + driver.command_executor._url)
    # 获取当前窗口的 session id
    current_session_id = driver.session_id
    driver_infos['session_id'] = current_session_id
    print("# 驱动Session：" + current_session_id)
    
    chrome_windows = None
    # 获取所有打开的窗口
    for window in gw.getWindowsWithTitle("Google Chrome"):
        # 切换到当前窗口
        try:
            window.activate()
        except gw.PyGetWindowException:
            pass
        # 获取当前窗口的 session id
        current_window_session_id = driver.session_id
        # 如果 session id 匹配，将窗口添加到列表
        if current_window_session_id == current_session_id:
            chrome_windows = window
            break
        
    # 获取所有打开的窗口
    vscode_windows = None
    windows = gw.getWindowsWithTitle("Visual Studio Code")
    vscode_windows = windows[0]
    
    iMaxCount = 0
    idx = 0
    is_reload = False
    while idx < length_templates:
        if iMaxCount > 25:
            break
        relative_path = list_templates[idx]
        template_path = TEMPALTES_BASE_PATH + relative_path
        need_totranslate = checkout_template_translation(template_path)
        if need_totranslate == False and is_reload == False:
            print("# 模板文件已经完成翻译：" + template_path)
            is_reload == False
            idx += 1
            continue
        else:
            pass
        if is_reload == False:
            print("# 模板文件需要进行翻译" + template_path)
            origin_path = ORIGIN_BASE_PATH + relative_path
            if not os.path.exists(origin_path):
                for rep_chars in [('ue', 'ü'), ('oe', 'ö'), ('ae', 'ä'), ('Ue', 'Ü'), ('Oe', 'Ö'), ('Ae', 'Ä'), ('ss', 'ß')]:
                    origin_path = origin_path.replace(rep_chars[0], rep_chars[1])
                    if os.path.exists(origin_path):
                        break
                else:
                    print("# 相应的原始文件未找到：" + origin_path)
                    is_reload == False
                    idx += 1
                    continue
            url_full = f"{origin_path}"
            try:
                driver.get(url_full)
            except:
                input(">>> 程序错误，任意键退出")
                break
            time.sleep(1)
            actions = ActionChains(driver)
            # 等待页面中的某个元素出现，例如，这里等待一个 id 为 "myElement" 的元素
            time.sleep(1)
            # 鼠标右键菜单
            # 如果找到 Chrome 窗口，则激活它
            if chrome_windows:
                try:
                    chrome_windows.activate()
                except gw.PyGetWindowException:
                    pass
            actions.context_click().perform()
            time.sleep(1)
            pyautogui.typewrite(['up', 'up', 'up'])
            pyautogui.typewrite(['return'])
            time.sleep(8)
        else:
            print("# 模板文件需要进行校验" + template_path)
            url_full = f"http://127.0.0.1:8000{relative_path}"
            url_full = url_full.replace('\\', '/')
            try:
                driver.get(url_full)
            except:
                input(">>> 程序错误，任意键退出")
                break
            print("-" * 20)
        if False:
            while True:
                if vscode_windows:
                    try:
                        vscode_windows.activate()
                    except gw.PyGetWindowException:
                        pass
                user_input = input(">>> 请输入操作内容（输入 'exit' 退出循环， 'c' 继续， 'n' 下一个页面）: ")
                if user_input in ['exit', 'c', 'n']:
                    break
            if user_input == 'exit':
                print("退出循环。")
                break
            elif user_input == 'c':
                print("# 执行操作 continue, 完成翻译执行操作，获取翻译的页面内容。")
                # input(">>> 执行操作 continue中，请再次确定页面是否完成翻译，任意继续当前操作: ")
                # 获取页面源代码
                page_source = driver.page_source
                # 使用 BeautifulSoup 解析页面源代码
                soup = BeautifulSoup(page_source, 'html.parser')
                # 找到要删除的 script 元素，假设要删除 src 为 "../ehlpdhtm.js" 的 script
                script_to_remove = soup.find('script', {'src': '../ehlpdhtm.js'})
                # 如果找到了对应的 script 元素，则移除
                if script_to_remove:
                    script_to_remove.decompose()
                # 找到要删除的 div，假设要删除 id 为 "div2" 的 div
                div_to_remove = soup.find('div', {'id': 'goog-gt-tt'})
                if div_to_remove:
                    div_to_remove.decompose()
                # 打印 <body> 内容
                # 提取页面的 <body> 内容
                body_content = soup.body
                formatted_html = body_content.prettify()
                with open("translated.body", "w", encoding='utf-8') as tf:
                    body_string = str(formatted_html)
                    fixed_result = body_string.replace("ä", "ae")
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
                    fixed_result = fixed_result.replace('\u00a0', '&nbsp;')
                    fixed_result = fixed_result.replace('<body>\n', '')
                    fixed_result = fixed_result.replace('</body>', '')
                    tf.write(fixed_result)
                # 尝试自动替换template的页面内容
                origin_conetnt = ""
                with open(template_path, "r", encoding='utf-8') as tpr:
                    origin_conetnt = tpr.read()
                origin_conetnt = origin_conetnt.lstrip('\n')
                pattern = re.compile(r'{% block mainbody %}\n.*?\n{% endblock %}', re.DOTALL)
                updated_html = pattern.sub("{% block mainbody %}\n" + fixed_result + "\n{% endblock %}", origin_conetnt)
                with open(template_path, "w", encoding='utf-8') as tpw:
                    tpw.write(updated_html)
                # print(body_content)
                # input(">>> 执行操作 continue中，请确保body已经更新至模板，任意继续当前操作: ")
                #
                is_reload = True
            elif user_input == 'n':
                print("# 执行操作 next。")
                #
                idx += 1
                # 执行操作 2 的代码
                is_reload = False
                print("=" * 20)
            else:
                is_reload = False
                print("# 未知操作，请重新输入。")
        else:
            if is_reload == False:
                print("# 执行操作 continue, 完成翻译执行操作，获取翻译的页面内容。")
                # 获取页面源代码
                page_source = driver.page_source
                # 使用 BeautifulSoup 解析页面源代码
                soup = BeautifulSoup(page_source, 'html.parser')
                # 找到要删除的 script 元素，假设要删除 src 为 "../ehlpdhtm.js" 的 script
                script_to_remove = soup.find('script', {'src': '../ehlpdhtm.js'})
                # 如果找到了对应的 script 元素，则移除
                if script_to_remove:
                    script_to_remove.decompose()
                # 找到要删除的 div，假设要删除 id 为 "div2" 的 div
                div_to_remove = soup.find('div', {'id': 'goog-gt-tt'})
                if div_to_remove:
                    div_to_remove.decompose()
                # 打印 <body> 内容
                # 提取页面的 <body> 内容
                body_content = soup.body
                formatted_html = body_content.prettify()
                with open("translated.body", "w", encoding='utf-8') as tf:
                    body_string = str(formatted_html)
                    fixed_result = body_string.replace("ä", "ae")
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
                    fixed_result = fixed_result.replace('\u00a0', '&nbsp;')
                    fixed_result = fixed_result.replace('<body>\n', '')
                    fixed_result = fixed_result.replace('</body>', '')
                    tf.write(fixed_result)
                # 尝试自动替换template的页面内容
                origin_conetnt = ""
                with open(template_path, "r", encoding='utf-8') as tpr:
                    origin_conetnt = tpr.read()
                origin_conetnt = origin_conetnt.lstrip('\n')
                pattern = re.compile(r'{% block mainbody %}\n.*?\n{% endblock %}', re.DOTALL)
                bAutoFix = True
                errMsg = ''
                replaceChar = ''
                toFixChar = ''
                while bAutoFix:
                    try:
                        if toFixChar != "" and replaceChar != "":
                            origin_conetnt = origin_conetnt.replace(replaceChar, toFixChar)
                            fixed_result = fixed_result.replace(replaceChar, toFixChar)
                        updated_html = pattern.sub("{% block mainbody %}\n" + fixed_result + "\n{% endblock %}", origin_conetnt)
                        bAutoFix = False
                    except Exception as e:
                        errMsg = e.msg
                        if 'bad escape' in errMsg:
                            replaceChar = errMsg.replace('bad escape ', '')
                            if '\\' in replaceChar:
                                toFixChar = replaceChar.replace('\\', '/')
                                continue
                        raise ("无法自动处理的错误" + errMsg)
                with open(template_path, "w", encoding='utf-8') as tpw:
                    tpw.write(updated_html)
                # print(body_content)
                #
                is_reload = True
            else:
                print("# 执行操作 next。")
                iMaxCount += 1
                idx += 1
                # 执行操作 2 的代码
                is_reload = False
                print("=" * 20)
                time.sleep(5)
    # 关闭浏览器
    driver.quit()

def main():
    message_file = os.path.join(settings.BASE_DIR, "locale", 'zh_hans', "LC_MESSAGES", "django.po")
    # generate_messages_records(message_file)
    root_path, dummy_dir = os.path.split(settings.BASE_DIR)
    message_records = os.path.join(root_path, 'messages.records')
    # translate_messages_records(msgrecords_path=message_records)
    update_messages_pofile(message_file, message_records)
    
if __name__ == '__main__':
    main()