# Create your models here.
from django.db import models
from django.contrib.auth.models import User

# Create your models here.
class Enigme(models.Model):
    numero = models.IntegerField()
    nom = models.CharField(max_length=50)
    question = models.TextField()
    image = models.CharField(max_length=40, default="default.png")
    solution = models.CharField(max_length=50)

    def update(self):
        self.save()

    def __str__(self) -> str:
        return self.nom


class Reponse(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    enigme = models.ForeignKey("Enigmes.Enigme", on_delete=models.CASCADE)
    reponse = models.CharField(max_length=50)
    validee = models.BooleanField(default=False)

    class Meta:
        unique_together = (("user", "enigme"),)

    def update(self):
        self.save()

    def __str__(self) -> str:
        return f"{self.user} a repondu {self.reponse} à la question {self.enigme}"


class Final(models.Model):
    code = models.CharField("Code", max_length=10)

    class Meta:
        verbose_name = ("Final")
        verbose_name_plural = ("Finals")

    def __str__(self):
        return self.code

    def get_absolute_url(self):
        return reverse("Final_detail", kwargs={"pk": self.pk})
