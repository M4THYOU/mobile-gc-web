from django import forms
from django.contrib.auth import authenticate
from django.contrib.auth.forms import UserChangeForm

import re

from .models import User


class CustomUserChangeForm(UserChangeForm):
    class Meta:
        fields = ()
        model = User


class LoginForm(forms.ModelForm):

    class Meta:
        model = User
        fields = ('username', 'password')

    def clean(self):
        username = self.cleaned_data.get('username')
        password = self.cleaned_data.get('password')
        user = authenticate(username=username, password=password)
        if not user or not user.is_active:
            raise forms.ValidationError("Sorry, that was invalid. Please try again.")

        return self.cleaned_data

    def get_auth_user(self):
        username = self.cleaned_data.get('username')
        password = self.cleaned_data.get('password')
        user = authenticate(username=username, password=password)
        return user


class RegisterForm(forms.ModelForm):

    class Meta:
        model = User
        fields = ('first_name', 'last_name', 'username', 'password')

    def clean(self):
        first_name = self.cleaned_data.get('first_name')
        last_name = self.cleaned_data.get('last_name')

        if first_name == '' or last_name == '':
            raise forms.ValidationError('First and last name required.')

        return self.cleaned_data

    def clean_username(self):
        email = self.cleaned_data.get('username')
        if not re.fullmatch('\S+@\S+\.\S+', email):
            raise forms.ValidationError('Invalid email address.')

        return email
