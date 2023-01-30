import json
import uuid

from django.shortcuts import render, HttpResponse, redirect
from app01.myform import MyRegForm
from django.http import JsonResponse
from app01 import models
from PIL import Image, ImageDraw, ImageFont
import random
from io import BytesIO
from django.contrib import auth
from django.contrib.auth.decorators import login_required
from django.db.models import Count
from django.db.models.functions import TruncMonth
from django.db.models import F
from bs4 import BeautifulSoup
from BBS import settings
import os


def register(request):
    reg_form = MyRegForm()
    if request.method == 'POST':
        back_dic = {'code': 1000, 'msg': ''}
        reg_form = MyRegForm(request.POST)
        if reg_form.is_valid():
            clean_data = reg_form.cleaned_data
            clean_data.pop('re_password')  # 弹出确认的密码，方便后面直接用字典传参
            file_obj = request.FILES.get('avatar')
            # 原来的form组件里没有文件的信息，所以需要单独加。但是文件路径不能为空，如果用户没有选择图片的话，就默认default，这种情况下应该不传值，而不是传null
            # 如果用户没有选择图片，不传值，使数据库的avatar字段为default值
            if file_obj:
                clean_data['avatar'] = file_obj
            # 用create_user在保存用户信息时，密码会加密处理
            models.UserInfo.objects.create_user(**clean_data)  # 利用字典进行关键字传值
            back_dic['url'] = '/logon/'
        else:
            back_dic['code'] = 2000
            back_dic['msg'] = reg_form.errors
        return JsonResponse(back_dic)
    return render(request, 'register.html', locals())


def login(request):
    if request.method == 'POST':
        back_dic = {'code': 1000, 'msg': ''}
        if request.POST.get('code') != request.session.get('code'):
            back_dic['code'] = 2000
            back_dic['msg'] = '验证码错误'
            return JsonResponse(back_dic)
        username = request.POST.get('username')
        password = request.POST.get('password')
        user_obj = auth.authenticate(request, username=username, password=password)
        if user_obj:
            # 保存用户登陆状态，之后就可以用request.user取到user_obj了
            auth.login(request, user_obj)
            back_dic['url'] = '/home/'
        else:
            back_dic['code'] = 3000
            back_dic['msg'] = '用户名或密码错误'
        return JsonResponse(back_dic)
    return render(request, 'login.html', locals())


def get_random():
    return random.randint(0, 255), random.randint(0, 255), random.randint(0, 255)


def get_code(request):
    img_obj = Image.new('RGB', (550, 35), get_random())
    img_draw = ImageDraw.Draw(img_obj)
    img_font = ImageFont.truetype('static/font/font1.ttf', 30)
    # 生成验证码
    code = ''
    for i in range(5):
        random_upper = chr(random.randint(65, 90))
        random_lower = chr(random.randint(97, 122))
        random_num = str(random.randint(0, 9))  # 这里必须是str，才能写入img中
        temp = random.choice([random_num, random_upper, random_lower])
        img_draw.text((i * 60 + 60, -2), temp, get_random(), img_font)
        code += temp
    request.session['code'] = code
    print(code)
    io_obj = BytesIO()
    img_obj.save(io_obj, 'png')
    return HttpResponse(io_obj.getvalue())


@login_required
def home(request):
    article_queryset = models.Article.objects.all()
    return render(request, 'home.html', locals())


def set_pwd(request):
    if request.method == 'POST':
        back_dict = {'code': 100, 'msg': ''}
        old_pwd = request.POST.get('old_pwd')
        new_pwd = request.POST.get('new_pwd')
        if request.user.check_password(old_pwd):
            request.user.set_password(new_pwd)
            request.user.save()  # 修改完后别忘了保存
            back_dict['msg'] = '修改成功'
        else:
            back_dict['code'] = 101
            back_dict['msg'] = '原密码错误'
        return JsonResponse(back_dict)


def logout(request):
    auth.logout(request)
    return redirect('/login/')


def site(request, username, **kwargs):
    user_obj = models.UserInfo.objects.filter(username=username).first()
    if not user_obj:
        return render(request, 'error.html', locals())
    blog = user_obj.blog
    # 查询用户所有的文章
    article_queryset = models.Article.objects.filter(blog=blog)
    # https: // www.cnblogs.com / jason / tag / 1 / 标签
    # https: // www.cnblogs.com / jason / category / 1
    # 分类
    # https: // www.cnblogs.com / jason / archive / 2020 - 11 / 日期
    if kwargs:
        # 针对不同的筛选条件，只要改变要展示的文章列表就可以了
        param = kwargs.get('param')
        condition = kwargs.get('condition')
        if condition == 'tag':
            # 双下划线实现跨表查询
            article_queryset = article_queryset.filter(tag__id=param)
            # 如果字段对应的是ForeignKey 那么会orm会自动在字段的后面加_id
        elif condition == 'category':
            article_queryset = article_queryset.filter(category_id=param)
        else:
            year, month = param.split('-')
            article_queryset = article_queryset.filter(create_time__month=month, create_time__year=year)

    # 以下内容加载到inclusion_tag内置标签里了
    # # 获取用户每个分类的文章数,按照cate分类取count
    # category_list = models.Category.objects.filter(blog=blog).annotate(count=Count('article__pk')).values_list('type_name', 'count', 'pk')
    # # 获取用户每个标签的文章数,按照标签分类取count
    # tag_list = models.Tag.objects.filter(blog=blog).annotate(count=Count('article')).values_list('tag_name', 'count', 'pk')
    # # 按照年月分组展现文章数量
    # time_list = models.Article.objects.filter(blog=blog).annotate(month=TruncMonth('create_time')).values('month').annotate(count=Count('pk')).values_list('month', 'count')
    return render(request, 'site.html', locals())


def article_detail(request, username, article_id):
    article_obj = models.Article.objects.filter(pk=article_id, blog__userinfo__username=username).first()
    blog = models.Blog.objects.filter(userinfo__username=username).first()
    comment_list = models.UserInfo2Article.objects.filter(article=article_obj)
    return render(request, 'article_detail.html', locals())


def up_or_down(request):
    # 1.没登录先登陆
    # 2.每个用户只能点一次赞或踩
    # 3.不能给自己点赞或踩.
    if request.is_ajax():
        back_dic = {'code': 1000, 'msg': ''}
        if request.user.is_authenticated():
            username = request.user.username
            user_obj = models.UserInfo.objects.filter(username=username).first()
            article_id = request.POST.get('article_id')
            article_obj = models.Article.objects.filter(pk=article_id).first()
            is_up = request.POST.get('is_up')
            is_up = json.loads(is_up)#将前端的的json格式转为python
            if not models.UserInfo2Article.objects.filter(username_id=user_obj.id, article_id=article_id, comment=None):
                if not models.Article.objects.filter(pk=article_id).values('blog__userinfo__username') == username:
                    back_dic['msg'] = '评价成功'
                    models.UserInfo2Article.objects.create(username=user_obj, article=article_obj, up_or_down=is_up)
                    if is_up:
                        models.Article.objects.filter(pk=article_id).update(up_num=F('up_num')+1)
                    else:
                        models.Article.objects.filter(pk=article_id).update(down_num=F('down_num')+1)
                else:
                    back_dic['code'] = 1001
                    back_dic['msg'] = '不能给自己的文章评价'
            else:
                back_dic['code'] = 1002
                back_dic['msg'] = '你已经评价过这篇文章了'
        else:
            back_dic['code'] = 1003
            back_dic['msg'] = '请先登陆'
        print(back_dic.get('code'))
        return JsonResponse(back_dic)


def secret(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        pass
    return render(request, 'secret.html')


def comment(request):
    if request.is_ajax():
        back_dic = {'code': 1000, 'msg': ''}
        if not request.user.is_authenticated():
            back_dic['code'] = 1001
            back_dic['msg'] = '请先登陆'
            return JsonResponse(back_dic)
        comment = request.POST.get('comment')
        parent_id = request.POST.get('parent_id')
        if parent_id:
            parent_obj = models.UserInfo2Article.objects.filter(pk=parent_id).first()
        else:
            parent_obj = None
        article_id = request.POST.get('article_id')
        user_obj = request.user
        article_obj = models.Article.objects.filter(pk=article_id).first()
        # 判断数据库中是否存在该记录
        models.UserInfo2Article.objects.create(username=user_obj, article=article_obj, comment=comment, up_or_down=True, parent_comment=parent_obj)
        back_dic['msg'] = comment
        back_dic['username'] = request.user.username
        if parent_obj:
            back_dic['parent'] = models.UserInfo2Article.objects.filter(pk=parent_id).values_list('username__username').first()[0]
        return JsonResponse(back_dic)


def backend(request):
    article_list = models.Article.objects.filter(blog__userinfo=request.user)
    return render(request, 'backend/backend.html', locals())


def add_article(request):
    if request.method == 'POST':
        title = request.POST.get('title')
        content = request.POST.get('content')
        blog = request.user.blog
        tag_id_list = request.POST.getlist('tag')
        category_id = request.POST.get('category')
        soup = BeautifulSoup(content, 'html.parser')
        # 处理用户可能输入的html代码中的script标签，防止XSS弹窗攻击
        tags = soup.find_all()
        for tag in tags:
            if tag.name == 'script':
                tag.decompose()# 这里的tag应该是soup中的应用，可以将删除同步到soup里
        content = str(soup)
        # 处理文章简介，截取文本的前150个字符
        brief = soup.text[0: 10]
        article_obj = models.Article.objects.create(
            brief=brief,
            art_title=title,
            content=content,
            blog=blog,
            category_id=category_id
        )
        # 由于标签和文章时多对多的关系，故需要在另一张关系表进行操作。且因为有多条数据，采用批量插入效率高
        tag2article_list = []
        for tag_id in tag_id_list:
            tag2article_list.append(models.Article2Tag(article=article_obj, tag_id=tag_id))
        models.Article2Tag.objects.bulk_create(tag2article_list)
        return redirect('/backend/')
    user_obj = request.user
    category_list = models.Category.objects.filter(blog__userinfo=user_obj)
    tag_list = models.Tag.objects.filter(blog__userinfo=user_obj)
    return render(request, 'backend/add_article.html', locals())


def look_comment(request):
    return render(request, 'backend/backend.html', locals())


def add_article_img(request):
    back_dic = {'error': 0}
    if request.method == 'POST':
        img_obj = request.FILES.get('imgFile')
        file_name = str(uuid.uuid4()) + img_obj.name# 这里是图片的存储地址
        file_path = os.path.join(settings.BASE_DIR, 'media', 'article_img', file_name)
        with open(file_path, 'wb') as f:
            for line in img_obj.chunks():
                f.write(line)
        # 这里写的是资源开放的接口，记得在最前面加/。这里的url就是传到编辑器的图片，编辑器生成的html代码的img标签的url的值，存在用户数据库的content字段(里面是html代码)里，所以得写个开放接口的路径
        back_dic['url'] = '/media/article_img/%s' % file_name
    return JsonResponse(back_dic)


def set_avatar(request):
    username = request.user.username
    if request.method == 'POST':
        file_obj = request.FILES.get('new_avatar')
        request.user.avatar = file_obj
        request.user.save()
        return redirect('/home/', locals())
    return render(request, 'set_avatar.html', locals())
