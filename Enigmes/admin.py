# Register your models here.
from django.contrib import admin
from Enigmes.models import *


# Register your models here.
class ThemeAdmin(admin.ModelAdmin):
    list_display = ('nom',)

class EnigmeAdmin(admin.ModelAdmin):
    list_display = ('numero', 'theme', 'nom', 'solution')


class ReponseAdmin(admin.ModelAdmin):
    list_display = ('user', 'enigme', 'validee')


class FinalAdmin(admin.ModelAdmin):
    list_display = ('theme','code')


admin.site.register(Enigme, EnigmeAdmin)
admin.site.register(Theme, ThemeAdmin)
admin.site.register(Reponse, ReponseAdmin)
admin.site.register(Final, FinalAdmin)
