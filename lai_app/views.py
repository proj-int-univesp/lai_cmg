from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import TemplateView
from django.db import IntegrityError

from .forms import CidadaoForm

class MenuView(LoginRequiredMixin, TemplateView):
    template_name = 'lai_app/menu.html'

def registrar_cidadao(request):
    if request.method == 'POST':
        form = CidadaoForm(request.POST)
        if form.is_valid():
            try:
                form.save()
                messages.success(request, 'Conta criada com sucesso!')
                return redirect('/accounts/login/')  # Redirecionar para a página de login ou outra página desejada
            except IntegrityError:
                messages.error(request, 'O nome de usuário já existe. Por favor, escolha outro.')
        else:
            messages.error(request, 'Por favor, corrija os erros abaixo.')
    else:
        form = CidadaoForm()
    return render(request, 'registration/registrar_cidadao.html', {'form': form})
