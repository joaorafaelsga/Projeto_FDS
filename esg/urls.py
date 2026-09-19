from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('fale-conosco/', views.fale_conosco, name='fale_conosco'),
    path('quem-somos/', views.quem_somos, name='quem_somos'),
    path('empresa/', views.empresa, name='empresa'),
    path('projeto/', views.projeto, name='projeto'),
]