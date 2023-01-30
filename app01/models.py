from django.db import models
from django.contrib.auth.models import AbstractUser


# 创建思路：先写普通字段，再写关联字段
class UserInfo(AbstractUser):
    phone = models.CharField(max_length=16, verbose_name='电话号码', blank=True)#设置blank是为了案例django的admin管理中该字段可以为空
    create_time = models.DateField(auto_now_add=True, verbose_name='注册时间')
    avatar = models.FileField(upload_to='avatar/', default='avatar/default', verbose_name='用户头像')
    # 外键字段
    Article = models.ManyToManyField(to='Article',
                                     through='UserInfo2Article',
                                     through_fields=('username', 'article'))
    blog = models.OneToOneField(to='Blog', null=True)# 这里null为True是允许用户创建时先不创建自己的个人站点

    def __str__(self):
        return self.username


class Blog(models.Model):
    site_title = models.CharField(max_length=32, verbose_name='站点标题')
    site_name = models.CharField(max_length=32, verbose_name='站点名称')
    site_theme = models.CharField(max_length=64, verbose_name='站点样式文件路径')

    def __str__(self):
        return self.site_name


class Category(models.Model):
    type_name = models.CharField(max_length=32, verbose_name='文章分类名')
    blog = models.ForeignKey(to='Blog')

    def __str__(self):
        return self.type_name


class Tag(models.Model):
    tag_name = models.CharField(max_length=32, verbose_name='文章标签名')
    blog = models.ForeignKey(to='Blog')

    def __str__(self):
        return self.tag_name


class Article(models.Model):
    brief = models.CharField(max_length=64, verbose_name='文章简介')
    art_title = models.CharField(max_length=32, verbose_name='文章标题')
    content = models.TextField(verbose_name='文章内容')
    create_time = models.DateField(auto_now_add=True, verbose_name='文章创建时间')
    # 以下3个字段需要频繁访问，所以直接放在该表中，免得频繁跨表访问
    comment_num = models.IntegerField(verbose_name='评论数', default=0)
    up_num = models.IntegerField(verbose_name='点赞数', default=0)
    down_num = models.IntegerField(verbose_name='点踩数', default=0)
    # 外键字段
    blog = models.ForeignKey(to='Blog')
    tag = models.ManyToManyField(to='Tag',
                                 through='Article2Tag',
                                 through_fields=('article', 'tag'))
    category = models.ForeignKey(to='Category')

    def __str__(self):
        return self.art_title


class UserInfo2Article(models.Model):
    username = models.ForeignKey(to='UserInfo')
    article = models.ForeignKey(to='Article')
    up_or_down = models.BooleanField(verbose_name='赞或踩')
    comment = models.CharField(max_length=255, verbose_name='评论内容', null=True)
    comment_time = models.DateTimeField(auto_now_add=True, null=True)
    parent_comment = models.ForeignKey(to='self', null=True, verbose_name='根评论')

    class Meta:
        verbose_name_plural = '点赞的用户-文章表'

    def __str__(self):
        return self.username.__str__() + '--' + self.article.__str__()


class Article2Tag(models.Model):
    article = models.ForeignKey(to='Article')
    tag = models.ForeignKey(to='Tag')

    def __str__(self):
        return self.tag.__str__() + '--' + self.article.__str__()



