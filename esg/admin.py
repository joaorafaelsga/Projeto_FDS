from django.contrib import admin

from .models import Comentario, Diagnostico, Empresa, Pergunta, Resposta


admin.site.register(Empresa)
admin.site.register(Pergunta)
admin.site.register(Diagnostico)
admin.site.register(Resposta)
admin.site.register(Comentario)
