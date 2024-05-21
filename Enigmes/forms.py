from django import forms
from django.contrib.auth.models import User


class ReponseForm(forms.Form):
    reponse = forms.CharField(label="Reponse", max_length=100)


class CompteForm(forms.Form):
    ident = forms.CharField(label="Nom d’utilisateur", max_length=150, required=True)
    prenom = forms.CharField(label="Prénom", max_length=150, required=True)
    nom = forms.CharField(label="Nom", max_length=150, required=True)

class CreaCompteForm(forms.Form):
    identite = forms.CharField(label="Nom d’utilisateur", max_length=150, required=True)
    prenom = forms.CharField(label="Prénom", max_length=150, required=False)
    nom = forms.CharField(label="Nom", max_length=150, required=False)
    mdp = forms.CharField(label='Mot de passe', max_length=32, widget=forms.PasswordInput)
