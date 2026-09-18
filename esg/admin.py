from django.contrib import admin

from .models import Diagnostico, Empresa, Pergunta, Resposta


admin.site.register(Empresa)
admin.site.register(Pergunta)
admin.site.register(Diagnostico)
admin.site.register(Resposta)
