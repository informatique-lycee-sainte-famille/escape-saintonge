from django import forms
from django.contrib.auth.models import User


class ReponseForm(forms.Form):
    reponse = forms.CharField(label="Reponse", max_length=100)


class CompteForm(forms.Form):
    ident = forms.CharField(label="Identifiant", max_length=150, required=True)
    prenom = forms.CharField(label="Prénom", max_length=150, required=True)
    nom = forms.CharField(label="Nom", max_length=150, required=True)
    email = forms.EmailField(label="Mail", required=False)


class CreaCompteForm(forms.Form):
    identite = forms.CharField(label="Identifiant", max_length=150, required=True)
    prenom = forms.CharField(label="Prénom", max_length=150, required=True)
    nom = forms.CharField(label="Nom", max_length=150, required=True)
    email = forms.EmailField(label="Adresse Mail", required=False)
    mdp = forms.CharField(max_length=32, widget=forms.PasswordInput, label='Mot de passe')
