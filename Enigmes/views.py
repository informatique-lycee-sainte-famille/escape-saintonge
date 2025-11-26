from django.shortcuts import render, redirect
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.models import User
from django.contrib import messages
from django.utils import timezone
from datetime import datetime

from Enigmes.models import Enigme, Reponse, Final
from .forms import ReponseForm, CompteForm, CreaCompteForm


# Create your views here.
def redir(request):
    if request.session.get("theme"):
        return redirect(f"Enigmes/{request.session['theme']}")
    return redirect('Enigmes/intro')


def index(request, theme):
    request.session['theme'] = theme
    enigmes = Enigme.objects.filter(theme=theme).order_by('numero')
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
        final = Final.objects.filter(theme=theme)
        for digit in final[0].code:
            enigme = Enigme()
            enigme.validee = True
            enigme.numero = int(digit)
            enigme.nom = "Final"
            enigmes.append(enigme)
    return render(request, 'enigmes/enigmes.html', {'enigmes': enigmes, 'user': request.user})


# @login_required(login_url="connexion")
def detail_enigme(request,theme, ident):
    try:
        enigme = Enigme.objects.filter(theme=theme).get(numero=ident)
    except Enigme.DoesNotExist:
        return redirect('/')
    request.session['theme'] = theme
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
                reponse.history = timezone.now()
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
        user = authenticate(request,
                            username=request.POST["username"],
                            password=request.POST["password"])
        if user:
            login(request, user)
            return redirect("/")
        else:
            messages.error(request, "Connexion échouée, vérifie nom d'utilisateur et mot de passe")
    elif request.user.is_authenticated:
        return redirect("compte")
    form = AuthenticationForm()
    return render(request, 'enigmes/connexion.html', {"form": form})


def compte(request):
    return render(request, 'enigmes/compte.html')


def creation(request):
    if request.method == "POST":
        form = CreaCompteForm(request.POST)
        if form.is_valid():
            if User.objects.filter(username=form.cleaned_data["identite"]).exists():
                messages.error(request, 'Utilisateur déjà existant')
            else:
                user = User.objects.create_user(form.cleaned_data["identite"],
                                                'e@mail.com',
                                                form.cleaned_data["mdp"])
                user.save()
                messages.success(request, 'créé avec succès, connecte toi !')
                return redirect("connexion")
    else:
        form = CreaCompteForm()
    return render(request, 'enigmes/compte.html', {"form": form, "creation": True})


def deconnexion(request):
    theme = request.session.get('theme')
    logout(request)
    request.session['theme'] = theme
    return redirect("/")

def get_stats(request):
    stats_gen = []
    stats_rap = []
    chrono = []
    data = {}
    #objets de base
    enigmes = Enigme.objects.filter(theme=request.session['theme'])
    reponses = Reponse.objects.all()
    #Classement général
    classement_gen = {}
    # Les plus rapides
    classement_rap = {i: '***' for i in range(1, len(enigmes) + 1)}
    for e in enigmes:
        rep = reponses.filter(enigme=e, validee=True)
        print(rep)
        if rep.exists():
            first = rep[0]
            for r in rep:
                #pour le général
                if r.user.username in classement_gen.keys():
                    classement_gen[r.user.username] += 1 #un point pour chaque réponse validée
                else:
                    classement_gen[r.user.username] = 1
                #pour le plus rapide
                if not r.user.is_staff and r.history < first.history:
                    first = r
            classement_rap[first.enigme.numero] = first.user.username
    #data finale
    cla_gen_trie = dict(sorted(classement_gen.items(), key=lambda item: item[1], reverse=True))
    for key, value in cla_gen_trie.items():
        data["desc"] = key
        data["data"] = value
        stats_gen.append(dict(data))
    for key, value in classement_rap.items():
        data["desc"] = key
        data["data"] = value
        stats_rap.append(dict(data))
    # Chrono du compte
    if request.user.is_authenticated:
        time = timezone.now() - request.user.date_joined
        secondes = time.seconds % 60
        minute = time.seconds // 60 % 24
        hour = time.seconds // 3600
        chrono.append(f"{time.days} jours")
        chrono.append(f"{hour} heures")
        chrono.append(f"{minute} minutes")
        chrono.append(f"{secondes} secondes")
    return render(request, 'enigmes/stats.html', {"stats_gen": stats_gen, "stats_rap": stats_rap, "chrono":chrono})
