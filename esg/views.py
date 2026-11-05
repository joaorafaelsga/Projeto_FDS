from django.contrib import messages
from django.shortcuts import get_object_or_404, redirect, render

from .forms import (
    AvaliacaoForm, ComentarioForm, EmpresaForm, HistoricoAvaliacoesForm,
)
from .models import Diagnostico, Empresa, Pergunta

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
            # Mensagem de erro atualizada para combinar com o visual em vermelho do HTML
            messages.error(request, 'O formulário contém erros. Por favor, verifique os campos destacados.')

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


def avaliacao(request):
    form = AvaliacaoForm(request.POST if request.method == "POST" else None)
    if request.method == "POST" and form.is_valid():
        diagnostico = form.save()
        request.session["diagnostico_id"] = diagnostico.pk
        return redirect("resultado_avaliacao")

    pilares = []
    for valor, nome in Pergunta.Pilar.choices:
        campos = [
            form[f"pergunta_{pergunta.pk}"]
            for pergunta in form.perguntas if pergunta.pilar == valor
        ]
        if campos:
            pilares.append({"nome": nome, "campos": campos})

    return render(request, "esg/avaliacao.html", {
        "form": form,
        "pilares": pilares,
        "tem_empresas": Empresa.objects.exists(),
    })


def resultado_avaliacao(request, empresa_id=None, diagnostico_id=None):
    diagnosticos = Diagnostico.objects.select_related("empresa").filter(
        pontuacao_total__isnull=False,
        pontuacao_maxima__gt=0,
    ).exclude(nivel="")
    if diagnostico_id is None:
        diagnostico = diagnosticos.filter(
            pk=request.session.get("diagnostico_id")
        ).first()
        if diagnostico is None:
            return redirect("avaliacao")
    else:
        diagnostico = get_object_or_404(
            diagnosticos, pk=diagnostico_id, empresa_id=empresa_id
        )

    pilares = diagnostico.gerar_relatorio()
    plano_acao = sorted(
        pilares,
        key=lambda pilar: pilar["percentual"] if pilar["percentual"] is not None else 101,
    )
    return render(request, "esg/resultado_avaliacao.html", {
        "pilares": pilares,
        "plano_acao": plano_acao,
        "diagnostico": diagnostico,
        "percentual": diagnostico.pontuacao_total / diagnostico.pontuacao_maxima * 100,
    })


def historico_avaliacoes(request):
    form = HistoricoAvaliacoesForm(request.GET or None)
    empresa_selecionada = None
    diagnosticos = Diagnostico.objects.none()
    if form.is_valid():
        empresa_selecionada = form.cleaned_data["empresa"]
        diagnosticos = empresa_selecionada.diagnosticos.filter(
            pontuacao_total__isnull=False,
            pontuacao_maxima__gt=0,
        ).exclude(nivel="").order_by("-criado_em", "-pk")

    return render(request, "esg/historico_avaliacoes.html", {
        "form": form,
        "empresa_selecionada": empresa_selecionada,
        "diagnosticos": diagnosticos,
        "tem_empresas": Empresa.objects.exists(),
    })
