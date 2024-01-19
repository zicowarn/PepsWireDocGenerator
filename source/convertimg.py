import os
import re
from PIL import Image # pip install Pillow

'''
Created on 17.01.2024
Updated on 18.01.2024

@author: wang
'''

try:
    from myapp import settings  # @UnusedImport
except:
    pass

TRAIL = -1


def convert_gif_to_jpg(gif_path, jpg_path):
    try:
        # 打开 GIF 文件
        with Image.open(gif_path) as img:
            # 如果 GIF 文件只有一个帧，保存为 JPG
            if img.n_frames == 1:
                # 转换为适应性调色板模式
                img = img.convert("P", palette=Image.ADAPTIVE)
                img.convert("RGB").save(jpg_path, "JPEG")
                print(f"成功将 {gif_path} 转换为 {jpg_path}")
            else:
                print(f"{gif_path} 包含多个帧，忽略转换")
                return False
        os.remove(gif_path)
        return True
    except Exception as e:
        print(f"转换失败: {e}")
        return False
    
def update_h2t_records(gif_filename, jpg_filename, h2tcontent):
    # 使用正则表达式进行替换
    new_string = re.sub(gif_filename, jpg_filename, h2tcontent)
    return new_string

def convert_git2jpg_update_h2t(static_base_path, h2t_record_path):
    list_toconvert = []
    # traverse the list 
    for root, dirs, files in os.walk(static_base_path, topdown=False):
        if len(files) != 0:
            # iterate the files list
            for single_file in list(sorted(files)):
                # convert only htm files
                if not single_file.endswith('.gif'):
                    continue
                # set target path
                source_file = os.path.join(root, single_file)
                target_file = source_file.replace('.gif', '.jpg')
                list_toconvert.append((source_file, target_file))
    if len(list_toconvert) == 0:
        return False
    if os.path.exists(h2t_record_path):
        h2t_content = ""
        with open(h2t_record_path, 'r', encoding='utf-8') as fr:
            h2t_content = fr.read()
    else:
        h2t_content = ""
    
    for idx, tuple_convert in enumerate(list_toconvert):
        if TRAIL > 0 and idx > TRAIL:
            break
        rts = convert_gif_to_jpg(*tuple_convert)
        dummy_path, gif_filename = os.path.split(tuple_convert[0])
        dummy_path, jpg_filename = os.path.split(tuple_convert[1])
        if rts and h2t_content != "":
            h2t_content = update_h2t_records(gif_filename, jpg_filename, h2t_content)
    if os.path.exists(h2t_record_path):
        with open(h2t_record_path, 'w', encoding='utf-8') as fw:
            fw.write(h2t_content)
            
            
def update_templates_imgsize(templates_base_path):
    """change img node attribute height is auto, width is auto as default

    Args:
        static_base_path (_type_): _description_
        templates_base_path (_type_): _description_

    Returns:
        _type_: _description_
    """
    list_templates = []
    for root, dirs, files in os.walk(templates_base_path, topdown=False):
        if len(files) != 0:
            # iterate the files list
            for single_file in list(sorted(files)):
                # convert only htm files
                if not single_file.endswith('.htm'):
                    continue
                # set target path
                source_file = os.path.join(root, single_file)
                list_templates.append(source_file)
    if (list_templates) == 0:
        return False
    for file_templae in list_templates:
        print(f"# 正在处理模板: {file_templae}")
        template_content = ""
        is_updated = False
        with open(file_templae, 'r', encoding='utf-8') as fr:
            template_content = fr.read()
        patternwh = r'(<img[^>]*\s)width="\d+"'
        matchwh = re.search(patternwh, template_content)
        if matchwh :
            if matchwh:
                template_content = re.sub(patternwh, r'\1width="auto"', template_content)
            with open(file_templae, 'w', encoding='utf-8') as fw:
                fw.write(template_content)

def update_templates_imgsrc(static_base_path, templates_base_path):
    list_jpgimgaes = []
    for root, dirs, files in os.walk(static_base_path, topdown=False):
        if len(files) != 0:
            # iterate the files list
            for single_file in list(sorted(files)):
                # convert only htm files
                if not single_file.endswith('.jpg'):
                    continue
                # set target path
                source_file = os.path.join(root, single_file)
                ref_file = source_file.replace(static_base_path, '')
                fix_ref_file = ref_file.replace('\\', '../')
                list_jpgimgaes.append(fix_ref_file)
    if len(list_jpgimgaes) == 0:
        return False
    list_templates = []
    for root, dirs, files in os.walk(templates_base_path, topdown=False):
        if len(files) != 0:
            # iterate the files list
            for single_file in list(sorted(files)):
                # convert only htm files
                if not single_file.endswith('.htm'):
                    continue
                # set target path
                source_file = os.path.join(root, single_file)
                list_templates.append(source_file)
    if (list_templates) == 0:
        return False
    #
    list_nofound = []
    for file_templae in list_templates:
        print(f"# 正在处理模板: {file_templae}")
        if 'Das_Vorbereitungs' in file_templae:
            a = 0
        template_content = ""
        is_updated = False
        with open(file_templae, 'r', encoding='utf-8') as fr:
            template_content = fr.read()
        # 匹配 img 标签中的 src 属性值
        pattern = r'<img.+src="(.*?)"' # r'<img.+src="(.*?)"'
        imgmatches = re.findall(pattern, template_content, re.DOTALL)
        if len(imgmatches) == 0:
            continue
        for imgsrc in imgmatches:
            if not imgsrc.endswith('.gif'):
                continue
            else:
                is_replaced = False
                check_path = imgsrc.replace('.gif', '.jpg')
                check_path_nospaces = check_path.replace('%20', ' ')
                for jpg_file in list_jpgimgaes:
                    if jpg_file.endswith(check_path):
                        template_content = re.sub(imgsrc, check_path, template_content)
                        is_replaced = True
                        is_updated = True
                    elif jpg_file.endswith(check_path_nospaces):
                        template_content = re.sub(imgsrc, check_path, template_content)
                        is_replaced = True
                        is_updated = True
                    else:
                        pass
                if not is_replaced:
                    list_nofound.append(imgsrc)
        # 匹配 img 标签中的 src 属性值
        pattern = r'alt="(.*?)"'
        altmatches = re.findall(pattern, template_content)
        for altset in altmatches:
            if not altset.endswith('.gif'):
                continue
            else:
                check_path = altset.replace('.gif', '.jpg')
                for jpg_file in list_jpgimgaes:
                    if jpg_file.endswith(check_path):
                        template_content = re.sub(altset, check_path, template_content)
                    else:
                        pass
                a = 0
        if is_updated:
            with open(file_templae, 'w', encoding='utf-8') as fw:
                fw.write(template_content)
        else:
            pass
        print("# 未处理的 img src标识")
        for undoimg in list_nofound:
            print(f'src="{undoimg}"')


def main():
    static_base_path = os.path.join(settings.BASE_DIR, 'static')
    h2t_record_path = os.path.join(settings.BASE_DIR, 'htmlataghref.h2t')
    templates_base_path = os.path.join(settings.BASE_DIR, 'templates')
    # convert_git2jpg_update_h2t(static_base_path, h2t_record_path)
    update_templates_imgsrc(static_base_path, templates_base_path)
    # update_templates_imgsize(templates_base_path)
    
if __name__ == '__main__':
    main()