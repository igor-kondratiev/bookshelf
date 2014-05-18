# coding=utf-8
from django import forms
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError


class RegistrationForm(forms.Form):
    username = forms.CharField(max_length=16)
    email = forms.EmailField()
    password = forms.CharField(max_length=16)

    def clean_username(self):
        username = self.cleaned_data['username']
        if User.objects.filter(username=username).count() > 0:
            raise ValidationError('Пользователь с таким именем уже существует')

        return username

    def clean_email(self):
        email = self.cleaned_data['email']
        if User.objects.filter(email=email).count() > 0:
            raise ValidationError('Пользователь с таким email уже существует')

        return email
