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
    from . import navimenu 
    context = { 'menudata': navimenu.menus }
    return render(request, 'main.html', context)
