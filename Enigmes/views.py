from django.shortcuts import render, redirect
from django.contrib.auth import login, logout
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.models import User
from django.contrib import messages
from django.utils import timezone
import datetime

from Enigmes.models import Enigme, Reponse, Final
from .forms import ReponseForm, CompteForm, CreaCompteForm


# Create your views here.
def redir(request):
    return redirect('Enigmes/')


def index(request):
    enigmes = Enigme.objects.all().order_by('numero')
    user = None
    finaliste = False
    if request.user.is_authenticated:
        finaliste = True
        reponses = Reponse.objects.filter(user=request.user).order_by("enigme")
        for e in enigmes:
            e.solution = ""
            reponse = reponses.filter(enigme=e)
            if reponse.exists() and reponse[0].validee:
                e.validee = True
            else:
                finaliste = False
    if finaliste:
        enigmes = []
        final = Final.objects.get(pk=1)
        for digit in final.code:
            enigme = Enigme()
            enigme.validee = True
            enigme.numero = int(digit)
            enigme.nom = "Final"
            enigmes.append(enigme)
    return render(request, 'enigmes/enigmes.html', {'enigmes': enigmes, 'user': request.user})


# @login_required(login_url="connexion")
def detail_enigme(request, ident):
    try:
        enigme = Enigme.objects.get(numero=ident)
    except Enigme.DoesNotExist:
        return redirect('/')
    reponse = Reponse()
    if request.user.is_authenticated:
        qResponse = Reponse.objects.filter(enigme=enigme, user=request.user)
        if qResponse.exists():
            reponse = qResponse[0]
        if not reponse.validee and request.method == "POST":
            form = ReponseForm(request.POST)
            if form.is_valid():
                if not reponse.reponse:
                    reponse = Reponse.objects.create(user=request.user, enigme=enigme)
                reponse.reponse = form.cleaned_data["reponse"]
                if reponse.reponse == enigme.solution:
                    reponse.validee = True
                reponse.save()
        else:
            form = ReponseForm()
            if reponse.reponse:
                form = ReponseForm(initial={"reponse": reponse.reponse})
    else:
        form = ReponseForm()
        if request.method == "POST":
            return redirect("connexion")
    enigme.solution = ""
    return render(request, 'enigmes/detail_enigme.html', {'enigme': enigme, "reponse": reponse, 'form': form})


def connexion(request):
    if request.method == "POST":
        form = AuthenticationForm(request, request.POST)
        if form.is_valid():
            login(request, form.get_user())
            return redirect("/")
    elif request.user.is_authenticated:
        return redirect("compte")
    else:
        form = AuthenticationForm()
    return render(request, 'enigmes/connexion.html', {"form": form})


def compte(request):
    user = request.user
    if request.method == "POST":
        user.first_name = request.POST["prenom"]
        user.last_name = request.POST["nom"]
        user.email = request.POST["email"]
        user.save()
    form = CompteForm(initial={"ident": user.username,
                               "prenom": user.first_name,
                               "nom": user.last_name,
                               "email": user.email})

    return render(request, 'enigmes/compte.html', {"form": form})


def creation(request):
    if request.method == "POST":
        form = CreaCompteForm(request.POST)
        if form.is_valid():
            if User.objects.filter(username=form.cleaned_data["identite"]).exists():
                messages.error(request, 'Utilisateur déjà existant')
            else:
                user = User.objects.create_user(form.cleaned_data["identite"],
                                                form.cleaned_data["email"],
                                                form.cleaned_data["mdp"])
                user.first_name = form.cleaned_data["prenom"]
                user.last_name = form.cleaned_data["nom"]
                user.save()
                return redirect("connexion")
    else:
        form = CreaCompteForm()
    return render(request, 'enigmes/compte.html', {"form": form, "creation": True})


def deconnexion(request):
    logout(request)
    return redirect("/")

def get_stats(request):
    stats_glob = []
    stats_comp = []
    data = {}
    enigmes = Enigme.objects.all().order_by('numero')
    reponses = Reponse.objects.all().order_by("enigme")
    users = User.objects.filter(is_active=True, is_staff=False)
    data["desc"] = "Pourcentage de bonnes réponses : "
    data["data"] = f"{len(reponses.filter(validee=True))/len(reponses)*100} %"
    stats_glob.append(dict(data))
    max = 0
    min = 0
    for user in users:
        cpt = 0
        for reponse in reponses.filter(user=user):
            if reponse.validee:
                cpt += 1
        tmp = cpt/len(enigmes)*100
        if tmp > max:
            max = tmp
        if tmp < min:
            min = tmp
    data["desc"] = "Taux de bonnes réponses max :"
    data["data"] = f"{max} %"
    stats_glob.append(dict(data))
    data["desc"] = "Taux de bonnes réponses min :"
    data["data"] = f"{min} %"
    stats_glob.append(dict(data))
    # données du compte
    data["desc"] = "Nombre de questions répondues :"
    data["data"] = f"{len(reponses.filter(user=request.user))} sur un total de {len(enigmes)}"
    stats_comp.append(dict(data))
    rep_val = len(reponses.filter(user=request.user, validee=True))/len(enigmes)*100
    data["desc"] = "Taux de bonnes réponses :"
    data["data"] = f"{rep_val} %"
    stats_comp.append(dict(data))
    time = timezone.now() - request.user.date_joined
    secondes = time.seconds % 60
    minute = time.seconds // 60 % 24
    hour = time.seconds // 3600
    data["desc"] = "Temps depuis le début de votre partie :"
    data["data"] = f"{time.days} jours, {hour} heures, {minute} minutes, {secondes} secondes"
    print(time, time.seconds)
    stats_comp.append(dict(data))
    return render(request, 'enigmes/stats.html', {"stats_glob": stats_glob, "stats_comp": stats_comp})