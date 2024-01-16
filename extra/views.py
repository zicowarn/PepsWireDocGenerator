'''
Created on 25.07.2021

@author: wang
'''
import os
import platform
from django.shortcuts import render, HttpResponse
from . import settings

def index(request):
    if request.path.endswith('htm'):
        context = {'encoding': 'utf-8' }
        target_template = request.path.replace('/', '', 1)
        current_os = platform.system()
        if current_os == "Windows":
            print("Running on Windows")
            target_template = target_template.replace('/', '\\')
        elif current_os == "Darwin":
            print("Running on macOS")
            target_template = target_template.replace('\\', '/')
        return render(request, target_template, context)
    elif request.path.endswith('css'):
        context = {'encoding': 'utf-8' }
        target_template = request.path.replace('/', '', 1)
        target_template = target_template.replace('/', '\\')
        return render(request, target_template, context, content_type="text/css")
    elif request.path.endswith('js'):
        context = {'encoding': 'utf-8' }
        target_template = request.path.replace('/', '', 1)
        target_template = target_template.replace('/', '\\')
        return render(request, target_template, context, content_type="application/x-javascript")
    elif request.path.endswith('jpg'):
        try:
            target_template = request.path.replace('/', '', 1)
            target_template = target_template.replace('/', '\\')
            imagepath = os.path.join(settings.BASE_DIR, "static/{}".format(target_template))  # 图片路径
            with open(imagepath, 'rb') as f:
                image_data = f.read()
            return HttpResponse(image_data, content_type="image/png")
        except Exception as e:
            print(e)
            return HttpResponse(str(e))
    elif request.path.endswith('gif'):
        try:
            target_template = request.path.replace('/', '', 1)
            target_template = target_template.replace('/', '\\')
            imagepath = os.path.join(settings.BASE_DIR, "static/{}".format(target_template))  # 图片路径
            with open(imagepath, 'rb') as f:
                image_data = f.read()
            return HttpResponse(image_data, content_type="image/png")
        except Exception as e:
            print(e)
            return HttpResponse(str(e))
    elif request.path.endswith('ico'):
        return HttpResponse(404)
    elif request.path.endswith('messages.html'):
        i_offset = int(request.GET.get('id', '20'))
        root_path, dummy_dir = os.path.split(settings.BASE_DIR)
        message_records = os.path.join(root_path, 'messages.records')
        if not os.path.exists(message_records):
            return HttpResponse(404)
        render_records = []
        origin_records = []
        with open(message_records, 'r', encoding='utf-8') as mr:
            origin_records = mr.readlines()
        if len(origin_records) == 0:
            return HttpResponse(404)
        try:
            for ln in origin_records:
                if len(render_records) == i_offset:
                    break
                fix_line = ln.rstrip('\n')
                tuple_record = eval(fix_line)
                if len(tuple_record) != 3:
                    continue
                translated_msg = tuple_record[2]
                if translated_msg == '':
                    render_records.append(tuple_record)
            if (render_records) == 0:
                return HttpResponse(404)
            context = { 'messages': render_records }
            return render(request, 'messages.html', context)
        except Exception as e:
            return HttpResponse(404)
    from . import navimenu 
    context = { 'menudata': navimenu.menus }
    return render(request, 'main.html', context)
