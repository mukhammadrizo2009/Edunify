from django import forms
from django.contrib.auth.forms import UserCreationForm
from .models import CustomUser


class ProfileEditForm(forms.ModelForm):
    first_name = forms.CharField(
        max_length=30,
        required=False,
        label='Ism',
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Ismingizni kiriting',
            'autocomplete': 'given-name',
        })
    )
    last_name = forms.CharField(
        max_length=150,
        required=False,
        label='Familiya',
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Familiyangizni kiriting',
            'autocomplete': 'family-name',
        })
    )
    bio = forms.CharField(
        required=False,
        label='Bio',
        widget=forms.Textarea(attrs={
            'class': 'form-control',
            'placeholder': "O'zingiz haqingizda qisqacha...",
            'rows': 3,
        })
    )
    phone = forms.CharField(
        max_length=20,
        required=False,
        label='Telefon raqam',
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': '+998 90 123 45 67',
            'autocomplete': 'tel',
        })
    )
    avatar = forms.ImageField(
        required=False,
        label='Profil rasmi',
        widget=forms.ClearableFileInput(attrs={
            'class': 'form-control',
            'accept': 'image/*',
        })
    )

    class Meta:
        model = CustomUser
        fields = ['first_name', 'last_name', 'bio', 'phone', 'avatar']


class RegisterForm(UserCreationForm):
    email = forms.EmailField(
        required=True,
        widget=forms.EmailInput(attrs={
            'class': 'form-control',
            'placeholder': 'example@email.com',
            'autocomplete': 'email',
        })
    )

    class Meta:
        model = CustomUser
        fields = ['username', 'email', 'password1', 'password2']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Style all fields
        for field_name, field in self.fields.items():
            field.widget.attrs.update({'class': 'form-control'})
        self.fields['username'].widget.attrs['placeholder'] = 'foydalanuvchi_nomi'
        self.fields['username'].widget.attrs['autocomplete'] = 'username'
        self.fields['password1'].widget.attrs['placeholder'] = '••••••••'
        self.fields['password1'].widget.attrs['autocomplete'] = 'new-password'
        self.fields['password2'].widget.attrs['placeholder'] = '••••••••'
        self.fields['password2'].widget.attrs['autocomplete'] = 'new-password'

    def save(self, commit=True):
        user = super().save(commit=False)
        user.email = self.cleaned_data['email']
        user.role = 'student'  # Always student, only admin can assign other roles
        if commit:
            user.save()
        return user


class LoginForm(forms.Form):
    identifier = forms.CharField(
        max_length=254,
        label='Foydalanuvchi nomi yoki email',
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'username yoki email',
            'autocomplete': 'username email',
        })
    )
    password = forms.CharField(
        label='Parol',
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': '••••••••',
            'autocomplete': 'current-password',
        })
    )
