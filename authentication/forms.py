from django import forms
from django.contrib.auth import get_user_model
from django.contrib.auth.forms import UserCreationForm
from django.utils.translation import gettext_lazy as _


class LoginForm(forms.Form):
    username = forms.CharField(max_length=63, label="Nom d'utilisateur")
    username.widget.attrs.update({'placeholder': _("Nom d'utilisateur"), 'class': 'input'})
    password = forms.CharField(max_length=63, widget=forms.PasswordInput, label="Mot de passe")
    password.widget.attrs.update({'placeholder': _("Mot de passe"), 'class': 'input'})

class SignupForm(UserCreationForm):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["username"].widget.attrs.update({'placeholder': _("Nom d'utilisateur"), 'class': 'input'})
        self.fields["password1"].widget.attrs.update({'placeholder': _("Mot de passe"), 'class': 'input'})
        self.fields["password2"].widget.attrs.update({'placeholder': _("Confirmer mot de passe"), 'class': 'input'})

    class Meta(UserCreationForm.Meta):
        model = get_user_model()
        fields = ("username", "password1", "password2")
