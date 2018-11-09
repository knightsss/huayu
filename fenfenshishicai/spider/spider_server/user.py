#coding=utf-8
__author__ = 'shifeixiang'
from django.views.decorators.csrf import csrf_exempt    #用于处理post请求出现的错误
from django.shortcuts import render_to_response
from spider_server.models import TaskUser
from append_purchase_tx_fenfen.models import ProbUser

@csrf_exempt
def set_user(request):

    try:
        user_name = request.POST['in_user']
        user_password = request.POST['in_pwd']
        control = request.POST['control']
        user_id = len(ProbUser.objects.all()) + 1
        user_status = False
        if(control == 'add'):
            obj_pro = ProbUser(user_id=user_id, user_name=user_name, user_password=user_password, user_status=user_status)
            obj_pro.save()
        if(control == 'delete'):
            ProbUser.objects.filter(user_name=user_name).delete()
        obj_pro = ProbUser.objects.all()
    except:
        obj_pro = ProbUser.objects.all()
        return render_to_response('set_user.html', {"obj_pro":obj_pro})

    return render_to_response('set_user.html', {"obj_pro":obj_pro})

