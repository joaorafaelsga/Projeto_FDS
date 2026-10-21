from django.contrib import messages
from django.shortcuts import redirect, render

from .forms import ComentarioForm, EmpresaForm

# Create your views here.
def home(request):
    return render(request, 'esg/home.html')

def fale_conosco(request):
    if request.method == 'POST':
        form = ComentarioForm(request.POST)

        if form.is_valid():
            form.save()
            messages.success(request, 'Mensagem enviada com sucesso!')
            return redirect('fale_conosco')
        else:
            messages.error(request, 'Erro no envio. Verifique se o e-mail ou os campos estão corretos.')

    else:
        form = ComentarioForm()

    return render(request, 'esg/fale_conosco.html', {'form': form})

def quem_somos(request):
    return render(request, 'esg/quem_somos.html')

def empresa(request):
    return render(request, 'esg/empresa.html')

def projeto(request):
    return render(request, 'esg/projeto.html')

def cadastrar_empresa(request):
    if request.method == 'POST':
        form = EmpresaForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "Empresa cadastrada com sucesso!")
            return redirect('cadastrar_empresa')
        else:
            messages.error(request, "Não foi possível realizar o cadastro. Verifique os campos pendentes abaixo.")
    else:
        form = EmpresaForm()
    
    return render(request, 'esg/cadastrar_empresa.html', {'form': form})