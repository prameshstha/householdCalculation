from crispy_forms.layout import Field, Layout
from django import forms
from django.contrib.auth.forms import UserCreationForm
from .models import accountUsers
from django.contrib.auth import authenticate

from crispy_forms.helper import FormHelper


class RegistrationForm(UserCreationForm):
    email = forms.EmailField(max_length=255, help_text='Required. Add a valid email address.')

    class Meta:
        model = accountUsers
        fields = ("email", "username", "first_name", "last_name", "password1", "password2")


class UserAuthenticationForm(forms.ModelForm):
    password = forms.CharField(label='Password', widget=forms.PasswordInput)

    class Meta:
        model = accountUsers
        fields = ('email', 'password')

    def clean(self):
        if self.is_valid():
            email = self.cleaned_data['email']
            password = self.cleaned_data['password']
            if not authenticate(email=email, password=password):
                raise forms.ValidationError('Invalid login details')


class AccountUpdateForm(forms.ModelForm):

    class Meta:
        model = accountUsers
        fields = ('username', 'first_name', 'last_name', 'pro_pic', 'user_dob', 'user_address')
        widgets = {
            'user_dob': forms.DateInput(
                                             attrs={'class': 'form-control', 'placeholder': 'Select a date',
                                                    'type': 'date'}),
        }

    def clean_email(self):
        if self.is_valid():
            email = self.cleaned_data['email']
            try:
                account = accountUsers.objects.exclude(pk=self.instance.pk).get(email=email)
            except accountUsers.DoesNotExist:
                return email
            raise forms.ValidationError('Email"%s" is already in use.' % account.email)

    def clean_username(self):
        if self.is_valid():
            username = self.cleaned_data['username']
            try:
                account = accountUsers.objects.exclude(pk=self.instance.pk).get(username=username)
            except accountUsers.DoesNotExist:
                return username
            raise forms.ValidationError('username"%s" is already in use.' % account.username)
