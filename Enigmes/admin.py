# Register your models here.
from django.contrib import admin
from Enigmes.models import Enigme, Reponse, Final


# Register your models here.
class EnigmeAdmin(admin.ModelAdmin):
    list_display = ('numero', 'nom', 'solution')


class ReponseAdmin(admin.ModelAdmin):
    list_display = ('user', 'enigme')


class FinalAdmin(admin.ModelAdmin):
    list_display = ('code',)


admin.site.register(Enigme, EnigmeAdmin)
admin.site.register(Reponse, ReponseAdmin)
admin.site.register(Final, FinalAdmin)
