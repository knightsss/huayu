# -*- coding: utf-8 -*-
"""spider URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/1.11/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  url(r'^$', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  url(r'^$', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.conf.urls import url, include
    2. Add a URL to urlpatterns:  url(r'^blog/', include('blog.urls'))
"""
from django.conf.urls import url
from django.contrib import admin
import spider_server.user,spider_server.user_huayu
import spider_server.main
import append_purchase_tx_fenfen.purchase_client_main
import append_predict_tx_fenfen.predict_main
import append_predict_tx_fenfen.report

urlpatterns = [
    url(r'^admin/', admin.site.urls),
    url(r'^set_user/$', spider_server.user.set_user),
    url(r'^auto_main/$', spider_server.main.auto_main),
    url(r'^control_auto_thread/$', spider_server.main.control_auto_thread),
    url(r'^test/$', spider_server.main.test),

    #预测
    url(r'^append_predict_main/$', append_predict_tx_fenfen.predict_main.predict_main),
    url(r'^append_control_predict_thread/$', append_predict_tx_fenfen.predict_main.control_predict_thread),

    #自动化购买
    url(r'^append_purchase/$', append_purchase_tx_fenfen.purchase_client_main.auto_admin),
    url(r'^append_purchase_control/$', append_purchase_tx_fenfen.purchase_client_main.control_probuser_thread),

    #for
    url(r'^get_append_predict_data/$', append_predict_tx_fenfen.predict_main.get_predict),

    url(r'^get_open_lottery/$', append_predict_tx_fenfen.predict_main.get_open_lottery),

    url(r'^append_predict_report/$', append_predict_tx_fenfen.report.predict_report),
    #'get_append_predict_data'
    # url(r'^set_user_huayu/$', spider_server.user_huayu.set_user),

    #删除当天数据
    url(r'^delete_append_kill_predict_current_date/$', append_predict_tx_fenfen.predict_main.delete_kill_predict_current_date),
]
