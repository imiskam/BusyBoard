from django.contrib.auth.forms import *
from captcha.fields import CaptchaField
from .models import *


class ContactForm(forms.Form):
    name = forms.CharField(required=True)
    phone = forms.CharField(required=True)
    email = forms.EmailField(required=True)
    message = forms.CharField(widget=forms.Textarea, required=True)
    captcha = CaptchaField()


class CustomUserCreationForm(UserCreationForm):
    first_name = forms.CharField(required=False, label='Name')
    last_name = forms.CharField(required=False, label='Surname')
    email = forms.EmailField(required=True)
    profile_photo = forms.ImageField(required=False)
    captcha = CaptchaField()

    class Meta:
        model = CustomUser
        fields = ("first_name", "last_name", "username", "email", "password1", "password2", "profile_photo", "captcha")

    def save(self, commit=True):
        user = super().save(commit=False)
        user.email = self.cleaned_data["email"]
        user.first_name = self.cleaned_data["first_name"]
        user.last_name = self.cleaned_data["last_name"]
        if 'profile_photo' in self.cleaned_data:
            user.profile_photo = self.cleaned_data["profile_photo"]
        if commit:
            user.save()
        return user


class UserProfileUpdateForm(forms.ModelForm):
    email = forms.EmailField()

    class Meta:
        model = CustomUser
        fields = ['username', 'email', 'first_name', 'last_name']


class PasswordChangingForm(PasswordChangeForm):
    old_password = forms.CharField(widget=forms.PasswordInput(attrs={'class': 'form-control', 'type': 'password'}))
    new_password1 = forms.CharField(widget=forms.PasswordInput(attrs={'class': 'form-control', 'type': 'password'}))
    new_password2 = forms.CharField(widget=forms.PasswordInput(attrs={'class': 'form-control', 'type': 'password'}))

    class Meta:
        model = CustomUser
        fields = ['old_password', 'new_password1', 'new_password2']
