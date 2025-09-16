from django import forms
from django.contrib.auth.models import User
from .models import Cidadao, PedidoInformacao

class CidadaoForm(forms.ModelForm):
    username = forms.CharField(max_length=150, label="Nome de Usuário")
    password = forms.CharField(widget=forms.PasswordInput, label="Senha")
    password_confirm = forms.CharField(widget=forms.PasswordInput, label="Confirmação de Senha")
    email = forms.EmailField(label="E-mail")

    class Meta:
        model = Cidadao
        fields = ['nome', 'num_doc_id', 'cep', 'logradouro', 'numero', 'complemento', 'bairro', 'cidade', 'estado', 'username', 'email', 'password']

    def clean(self):
        cleaned_data = super().clean()
        password = cleaned_data.get("password")
        password_confirm = cleaned_data.get("password_confirm")

        if password and password_confirm and password != password_confirm:
            self.add_error("password_confirm", "As senhas não coincidem.")

        return cleaned_data

    def save(self, commit=True):
        # Cria o usuário
        user = User.objects.create_user(
            username=self.cleaned_data['username'],
            password=self.cleaned_data['password'],
            email=self.cleaned_data['email']
        )
        # Associa o usuário ao Cidadão
        cidadao = super().save(commit=False)
        cidadao.credenciais = user
        if commit:
            cidadao.save()
        return cidadao

class AnaliseInicialForm(forms.ModelForm):

    class Meta:
        model = PedidoInformacao
        fields = ['setor_info']

class FornecInfoForm(forms.ModelForm):

    class Meta:
        model = PedidoInformacao
        fields = ['arquivo_info', 'observacoes_forn']

class ParecerPedInfoForm(forms.ModelForm):

    class Meta:
        model = PedidoInformacao
        fields = ['parecer']

class ReqInformacaoForm(forms.ModelForm):

    class Meta:
        model = PedidoInformacao
        fields = ['titulo', 'descricao']
        widgets = {
            'descricao': forms.Textarea(attrs={'rows': 5, 'cols': 40}),
        }

class RespostaPedInfoForm(forms.ModelForm):

    class Meta:
        model = PedidoInformacao
        fields = ['resp_inicial', 'just_resp_inicial']