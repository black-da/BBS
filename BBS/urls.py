"""BBS URL Configuration

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
from app01 import views
from BBS import settings
from django.views.static import serve

urlpatterns = [
    url(r'^admin/', admin.site.urls),
    url(r'^register/', views.register, name='register'),# name用于反向解析{% url 'register'%}
    url(r'^login/', views.login, name='login'),
    url(r'^get_code/', views.get_code),
    url(r'^$', views.home),# 首页，url为空时跳转到home
    url(r'^home/', views.home),
    url(r'^set_pwd', views.set_pwd, name='set_pwd'),
    url(r'set_avatar', views.set_avatar),
    url(r'^logout', views.logout, name='logout'),
    url(r'^up_or_down', views.up_or_down, name='up_or_down'),
    url(r'^secret/', views.secret, name='secret'),
    url(r'^comment', views.comment),
    url(r'^add/article', views.add_article),
    url(r'^add/media/article_img', views.add_article_img),
    url(r'^backend/', views.backend),
    url(r'^media/(?P<path>.*)', serve, {'document_root': settings.MEDIA_ROOT}),
    url(r'^(?P<username>\w+)/$', views.site, name='site'),#用到了有名分组，site就是blog，个人站点
    # 同一个视图函数，通过url携带不同的参数筛选不同的信息展示
    url(r'^(?P<username>\w+)/(?P<condition>category|tag|archive)/(?P<param>.*)/', views.site),
    # 文章详情页
    url(r'^(?P<username>\w+)/article/(?P<article_id>\d+)/', views.article_detail),

]
