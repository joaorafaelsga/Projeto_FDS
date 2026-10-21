from django import forms

from .models import Comentario, Empresa


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
            'nome': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Seu nome completo'}),
            'email': forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'seu@email.com'}),
            'assunto': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Assunto da mensagem'}),
            'mensagem': forms.Textarea(attrs={'class': 'form-control', 'rows': 5, 'placeholder': 'Sua mensagem'}),
        }