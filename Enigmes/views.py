from django.shortcuts import render, redirect
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.models import User
from django.contrib import messages
from django.utils import timezone

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
    logout(request)
    return redirect("/")

def get_stats(request):
    stats_gen = []
    stats_rap = []
    chrono = []
    data = {}
    #objets de base
    enigmes = Enigme.objects.all()
    reponses = Reponse.objects.all()
    users = User.objects.filter(is_active=True, is_staff=False)
    #Classement général
    classement = {}
    for user in users:
        classement[user.username] = len(reponses.filter(user=user, validee=True))
    tri = sorted(classement.items(), key=lambda x: x[1])
    tri.reverse()
    maximum = len(tri) if len(tri) < 10 else 10
    for i in range(maximum):
        data["desc"] = i+1
        data["data"] = f"{tri[i][0]}"
        stats_gen.append(dict(data))
    # Les plus rapides
    tri = reponses.filter(validee=True).order_by('enigme')
    classement = {i:'***' for i in range(1,len(enigmes)+1)}
    for rep in tri:
        if not rep.user.is_staff and classement[rep.enigme.numero] == '***':
             classement[rep.enigme.numero] = rep.user.username
    for key, value in classement.items():
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