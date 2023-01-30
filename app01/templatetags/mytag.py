"""
注册内置标签inclusion_tag,向内置标签的html传递后端信息
"""
from django import template
from app01 import models
from django.db.models import Count
from django.db.models.functions import TruncMonth


register = template.Library()


@register.inclusion_tag('left_menu.html')
def left_menu(username):
    user_obj = models.UserInfo.objects.filter(username=username).first()
    blog = user_obj.blog
    # 获取用户每个分类的文章数,按照cate分类取count
    category_list = models.Category.objects.filter(blog=blog).annotate(count=Count('article__pk')).values_list(
        'type_name', 'count', 'pk')
    # 获取用户每个标签的文章数,按照标签分类取count
    tag_list = models.Tag.objects.filter(blog=blog).annotate(count=Count('article')).values_list('tag_name', 'count',
                                                                                                 'pk')
    # 按照年月分组展现文章数量
    time_list = models.Article.objects.filter(blog=blog).annotate(month=TruncMonth('create_time')).values(
        'month').annotate(count=Count('pk')).values_list('month', 'count')

    return locals()


@register.inclusion_tag('left_category.html')
def left_category(user_obj):
    category_list = models.Category.objects.filter(blog__userinfo=user_obj)
    username = user_obj.username
    return locals()