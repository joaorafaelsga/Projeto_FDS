from django import forms
from django.db import transaction
from .models import Comentario, Diagnostico, Empresa, Pergunta, Resposta

class EmpresaForm(forms.ModelForm):
    class Meta:
        model = Empresa
        fields = ['nome', 'setor', 'porte', 'email_contato']
        widgets = {
            'nome': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Nome da Empresa'}),
            'setor': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Ex: Tecnologia, Varejo, Indústria'}),
            'porte': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Pequena, Média ou Grande'}),
            'email_contato': forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'contato@empresa.com'}),
        }

class ComentarioForm(forms.ModelForm):
    class Meta:
        model = Comentario
        fields = ["nome", "email", "assunto", "mensagem"]
        widgets = {
            'nome': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Seu nome completo', 'required': True}),
            'email': forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'seu@email.com', 'required': True}),
            'assunto': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Assunto da mensagem', 'required': True}),
            'mensagem': forms.Textarea(attrs={'class': 'form-control', 'rows': 5, 'placeholder': 'Sua mensagem', 'required': True}),
        }
        error_messages = {
            'email': {
                'invalid': 'Por favor, insira um e-mail com formato válido (ex: usuario@dominio.com).',
                'required': 'O campo de e-mail é obrigatório.'
            },
            'nome': {'required': 'O nome é obrigatório.'},
            'assunto': {'required': 'O assunto não pode ficar em branco.'},
            'mensagem': {'required': 'Por favor, escreva a sua mensagem.'}
        }

class AvaliacaoForm(forms.Form):
    empresa = forms.ModelChoiceField(
        queryset=Empresa.objects.order_by("nome"),
        label="Empresa",
        empty_label="Selecione a empresa",
        widget=forms.Select(attrs={"class": "form-control"}),
        error_messages={
            "required": "Selecione a empresa que será avaliada.",
            "invalid_choice": "Selecione uma empresa cadastrada.",
        },
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.perguntas = list(Pergunta.objects.order_by("pilar", "pk"))
        for pergunta in self.perguntas:
            self.fields[f"pergunta_{pergunta.pk}"] = forms.TypedChoiceField(
                label=pergunta.texto,
                choices=Resposta.Pontuacao.choices,
                coerce=int,
                widget=forms.RadioSelect,
                error_messages={
                    "required": "Responda esta pergunta antes de submeter a avaliação.",
                    "invalid_choice": "Selecione uma das opções apresentadas.",
                },
            )

    def clean(self):
        dados = super().clean()
        if not self.perguntas:
            raise forms.ValidationError(
                "O questionário ainda não possui perguntas disponíveis."
            )
        return dados

    @transaction.atomic
    def save(self):
        diagnostico = Diagnostico.objects.create(empresa=self.cleaned_data["empresa"])
        respostas = []
        for pergunta in self.perguntas:
            pontuacao = self.cleaned_data[f"pergunta_{pergunta.pk}"]
            respostas.append(Resposta(
                diagnostico=diagnostico,
                pergunta=pergunta,
                pontuacao=pontuacao,
                texto=Resposta.Pontuacao(pontuacao).label,
            ))
        Resposta.objects.bulk_create(respostas)
        diagnostico.calcular_pontuacao()
        return diagnostico


class HistoricoAvaliacoesForm(forms.Form):
    empresa = forms.ModelChoiceField(
        queryset=Empresa.objects.order_by("nome"),
        label="Empresa",
        empty_label="Selecione a empresa",
        widget=forms.Select(attrs={"class": "form-control"}),
        error_messages={
            "required": "Selecione uma empresa para consultar o histórico.",
            "invalid_choice": "Selecione uma empresa cadastrada.",
        },
    )
