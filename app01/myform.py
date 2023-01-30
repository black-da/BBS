"""
注册登陆的form组件的校验数据定义
"""
from django import forms
from app01 import models


class MyRegForm(forms.Form):
    username = forms.CharField(max_length=8, min_length=4, label='用户名',
                               error_messages={
                                   'required': '用户名不能为空',
                                   'max_length': '用户名最多8位',
                                   'min_length': '用户名最少4位',
                               },
                               widget=forms.widgets.TextInput(attrs={'class': 'form-control'}))
    password = forms.CharField(max_length=16, min_length=4, label='密码',
                               error_messages={
                                   'required': '密码不能为空',
                                   'max_length': '密码最多8位',
                                   'min_length': '密码最少4位',
                               },
                               widget=forms.widgets.PasswordInput(attrs={'class': 'form-control'}))
    re_password = forms.CharField(max_length=16, min_length=4, label='再次输入密码',
                                  error_messages={
                                      'required': '密码不能为空',
                                      'max_length': '密码最多8位',
                                      'min_length': '密码最少4位',
                                  },
                                  widget=forms.widgets.PasswordInput(attrs={'class': 'form-control'}))
    email = forms.EmailField(label='邮箱',
                             error_messages={
                                 'required': '邮箱不能为空',
                                 'invalid': '邮箱格式不正确',
                             },
                             widget=forms.widgets.EmailInput(attrs={'class': 'form-control'}))

    # hook函数进行二次验证
    def clean_username(self):
        username = self.cleaned_data.get('username')
        if models.UserInfo.objects.filter(username=username):
            self.add_error('username', '该用户名已存在')
        return username

    def clean(self):
        password = self.cleaned_data.get('password')
        re_password = self.cleaned_data.get('re_password')
        if not password == re_password:
            self.add_error('re_password', '两次密码输入不一致')
        return self.cleaned_data


