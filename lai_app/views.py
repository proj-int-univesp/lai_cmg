from datetime import datetime as dt, timedelta
from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import HttpResponseForbidden
from django.urls import reverse_lazy
from django.views.generic import DetailView, FormView, ListView, TemplateView
from django.db import IntegrityError

from .forms import (AnaliseInicialForm, CidadaoForm, FornecInfoForm, ParecerPedInfoForm, 
                    RecursoPrimInstForm, RecursoSegInstForm, ReqInformacaoForm, RespostaPedInfoForm, 
                    RespostaRecPrimInstForm, RespostaRecSegInstForm)
from .models import Configuracao, PedidoInformacao


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

class AnaliseInicialPedInfo(LoginRequiredMixin, FormView):

    form_class = AnaliseInicialForm
    template_name = 'lai_app/analise_inicial.html'
    success_url = reverse_lazy('ped_infos_analise')

    def dispatch(self, request, *args, **kwargs):

        ped_info = PedidoInformacao.objects.get(pk=self.kwargs['pk'])
        usuario = request.user
                
        if ( ped_info.situacao == 'AI' and 
            hasattr(usuario, 'funcionario') and
            usuario.funcionario.analisa_ped_info):

            return super().dispatch(request, *args, **kwargs)
        
        else:
            
            return HttpResponseForbidden("Você não tem permissão para acessar esta página."
                                        " Contate o administrador do sistema.")              
        
    def form_valid(self, form):
        
        ped_info = form.save(commit=False)
        ped_info.func_adm = self.request.user.funcionario
        ped_info.data_encam = dt.now()
        ped_info.situacao = 'BI' 

        ped_info.save()

        return super(AnaliseInicialPedInfo, self).form_valid(form)

    def get_context_data(self, **kwargs):
        # Adiciona o objeto ao contexto para exibir no template
        context = super().get_context_data(**kwargs)
        context['ped_info'] = PedidoInformacao.objects.get(pk=self.kwargs['pk'])
        
        return context

    def get_form_kwargs(self):
        # Adiciona o objeto ao form para ser validado
        kwargs = super().get_form_kwargs()
        kwargs['instance'] = PedidoInformacao.objects.get(pk=self.kwargs['pk'])
        
        return kwargs

class ConsultaMeusPedInfos(LoginRequiredMixin, ListView):

    model = PedidoInformacao
    template_name = 'lai_app/ped_infos_cidadao.html'
    context_object_name = 'ped_infos'

    def dispatch(self, request, *args, **kwargs):

        usuario = request.user
        
        if (hasattr(usuario, 'cidadao')):                        
            return super().dispatch(request, *args, **kwargs)
        else:
            return HttpResponseForbidden("Você não tem permissão para acessar esta página."
                                        " Contate o administrador do sistema.")  

    def get_queryset(self):

        queryset = PedidoInformacao.objects.filter(
            requerente=self.request.user.cidadao).order_by('data_pedido')
        
        return queryset

class ConsultaPedInfosAnaliseInicial(LoginRequiredMixin, ListView):

    model = PedidoInformacao
    template_name = 'lai_app/ped_infos_analise.html'
    context_object_name = 'ped_infos'

    def dispatch(self, request, *args, **kwargs):

        usuario = request.user

        if (hasattr(usuario, 'funcionario') and usuario.funcionario.analisa_ped_info):                        
            return super().dispatch(request, *args, **kwargs)
        else:
            return HttpResponseForbidden("Você não tem permissão para acessar esta página."
                                        " Contate o administrador do sistema.")  

    def get_queryset(self):
        # Obtém o queryset base

        queryset = PedidoInformacao.objects.filter(situacao='AI').order_by('data_pedido')
        
        return queryset

class ConsultaPedInfosFornecInfo(LoginRequiredMixin, ListView):

    model = PedidoInformacao
    template_name = 'lai_app/ped_infos_fornecimento.html'
    context_object_name = 'ped_infos'

    def dispatch(self, request, *args, **kwargs):

        usuario = request.user
        
        if (hasattr(usuario, 'funcionario')):                        
            return super().dispatch(request, *args, **kwargs)
        else:
            return HttpResponseForbidden("Você não tem permissão para acessar esta página."
                                        " Contate o administrador do sistema.")  

    def get_queryset(self):

        queryset = PedidoInformacao.objects.filter(
            situacao='BI',
            setor_info=self.request.user.funcionario.lotacao
        ).order_by('data_pedido')
        
        return queryset

class ConsultaPedInfosGeral(LoginRequiredMixin, ListView):

    model = PedidoInformacao
    template_name = 'lai_app/ped_infos_geral.html'
    context_object_name = 'ped_infos'

    def dispatch(self, request, *args, **kwargs):

        usuario = request.user

        if (hasattr(usuario, 'funcionario') and usuario.funcionario.analisa_ped_info):                        
            return super().dispatch(request, *args, **kwargs)
        else:
            return HttpResponseForbidden("Você não tem permissão para acessar esta página."
                                        " Contate o administrador do sistema.")  

    def get_queryset(self):
        # Obtém o queryset base

        queryset = PedidoInformacao.objects.all()
        
        # Obtém os parâmetros de filtro da URL (GET)
        numero = self.request.GET.get('numero')
        ano = self.request.GET.get('ano')
        requerente = self.request.GET.get('requerente')
        titulo = self.request.GET.get('titulo')
        data_inicio = self.request.GET.get('data_inicio')
        data_fim = self.request.GET.get('data_fim')
        situacao = self.request.GET.get('situacao')
        ordenacao = self.request.GET.get('ordenacao')

        filtros = 0
        
        if numero and numero.isdigit():
            queryset = queryset.filter(num_registro=int(numero))
            filtros += 1
        if ano and ano.isdigit():
            queryset = queryset.filter(data_pedido__year=int(ano))
            filtros += 1
        if data_inicio:
            queryset = queryset.filter(data_pedido__gte=data_inicio)
            filtros += 1
        if data_fim:
            queryset = queryset.filter(data_pedido__lte=data_fim)
            filtros += 1    
        if requerente:
            queryset = queryset.filter(requerente__nome__icontains=requerente)
            filtros += 1
        if titulo:
            queryset = queryset.filter(titulo__icontains=titulo)
            filtros += 1
        if situacao:
            queryset = queryset.filter(situacao=situacao)
            filtros += 1
        
        if ordenacao in ['data_pedido', '-data_pedido', 'requerente__nome', '-requerente__nome']:
            queryset = queryset.order_by(ordenacao)
        else:
            queryset = queryset.order_by('-data_pedido')

        if filtros == 0:
            queryset = queryset[:20]

        return queryset
    
    def get_context_data(self, **kwargs):
        # Adiciona os filtros ao contexto para manter os valores no template
        context = super().get_context_data(**kwargs)      

        context['filtros'] = self.request.GET
        context['ordenacao'] = self.request.GET.get('ordenacao', '-data_pedido')  # Ordenação padrão
        
        return context

class ConsultaPedInfosParecer(LoginRequiredMixin, ListView):

    model = PedidoInformacao
    template_name = 'lai_app/ped_infos_parecer.html'
    context_object_name = 'ped_infos'

    def dispatch(self, request, *args, **kwargs):

        usuario = request.user
        
        if (hasattr(usuario, 'funcionario') and
            usuario.funcionario.emite_parecer()):                        
            return super().dispatch(request, *args, **kwargs)
        else:
            return HttpResponseForbidden("Você não tem permissão para acessar esta página."
                                        " Contate o administrador do sistema.")  

    def get_queryset(self):

        queryset = PedidoInformacao.objects.filter(
            situacao='EP').order_by('data_pedido')
        
        return queryset
    
class ConsultaPedInfosRespInicial(LoginRequiredMixin, ListView):

    model = PedidoInformacao
    template_name = 'lai_app/ped_infos_resposta.html'
    context_object_name = 'ped_infos'

    def dispatch(self, request, *args, **kwargs):

        usuario = request.user
        
        if (hasattr(usuario, 'funcionario') and
            usuario.funcionario.responde_ped_info):                        
            return super().dispatch(request, *args, **kwargs)
        else:
            return HttpResponseForbidden("Você não tem permissão para acessar esta página."
                                        " Contate o administrador do sistema.")  

    def get_queryset(self):

        queryset = PedidoInformacao.objects.filter(
            situacao='DR').order_by('data_pedido')
        
        return queryset

class ConsultaPedInfosRecPrimInst(LoginRequiredMixin, ListView):

    model = PedidoInformacao
    template_name = 'lai_app/ped_infos_resp_rec_1.html'
    context_object_name = 'ped_infos'

    def dispatch(self, request, *args, **kwargs):

        usuario = request.user
        
        if (hasattr(usuario, 'funcionario') and
            usuario.funcionario.responde_recurso_1):                        
            return super().dispatch(request, *args, **kwargs)
        else:
            return HttpResponseForbidden("Você não tem permissão para acessar esta página."
                                        " Contate o administrador do sistema.")  

    def get_queryset(self):

        queryset = PedidoInformacao.objects.filter(
            situacao='AR').order_by('data_recurso_1')
        
        return queryset
    
class ConsultaPedInfosRecSegInst(LoginRequiredMixin, ListView):

    model = PedidoInformacao
    template_name = 'lai_app/ped_infos_resp_rec_2.html'
    context_object_name = 'ped_infos'

    def dispatch(self, request, *args, **kwargs):

        usuario = request.user
        
        if (hasattr(usuario, 'funcionario') and
            usuario.funcionario.responde_recurso_2):                        
            return super().dispatch(request, *args, **kwargs)
        else:
            return HttpResponseForbidden("Você não tem permissão para acessar esta página."
                                        " Contate o administrador do sistema.")  

    def get_queryset(self):

        queryset = PedidoInformacao.objects.filter(
            situacao='AF').order_by('data_recurso_2')
        
        return queryset

class DetalhesPedInfo(LoginRequiredMixin, DetailView):

    model = PedidoInformacao
    template_name = 'lai_app/detalhes_ped_info.html'
    context_object_name = 'ped_info'

    def dispatch(self, request, *args, **kwargs):

        usuario = request.user
        req = PedidoInformacao.objects.get(pk=self.kwargs['pk'])
        requerente = req.requerente
        config = Configuracao.objects.get(id=1)

        # Verifica se o usuário é o requerente do pedido
        if ((hasattr(usuario, 'cidadao') and requerente == usuario.cidadao) or 
        # Verifica se o usuário é funcionário
            (hasattr(usuario, 'funcionario') and  
        # Verifica se o usuário é funcionário e se pertence ao setor de análise de pedidos (administrativo)
            (usuario.funcionario.analisa_ped_info) or
        # Verifica a fase do processo e se o usuário é do setor responsável por fornecer a informação
            (req.situacao == 'BI' and req.setor_destino == usuario.funcionario.lotacao) or        
        # Verifica a fase do processo e se o usuário é do setor responsável por emitir o parecer
            (req.situacao == 'EP' and usuario.funcionario.lotacao == config.setor_parecer) or
        # Verifica a fase do processo e se o usuário é do setor responsável por definir a resposta
            (req.situacao == 'DR' and usuario.funcionario.lotacao == config.setor_resposta) or
        # Verifica a fase do processo e se o usuário é do setor responsável por analisar o recurso em 1ª instância
            (req.situacao == 'AR' and usuario.funcionario.lotacao == config.setor_recurso_1) or
        # Verifica a fase do processo e se o usuário é do setor responsável por analisar o recurso em 2ª instância
            (req.situacao == 'AF' and usuario.funcionario.lotacao == config.setor_recurso_2))):

            if(hasattr(usuario, 'cidadao')):
                if (req.prazo_recurso_1 is None and req.situacao == 'PR' and req.resp_inicial == False):
                    req.prazo_recurso_1 = dt.now() + timedelta(days=10)
                    req.save()
                if (req.prazo_recurso_2 is None and req.situacao == 'RR' and req.resp_recurso_1 == False):
                    req.prazo_recurso_2 = dt.now() + timedelta(days=10)
                    req.save()
            
            return super().dispatch(request, *args, **kwargs)            
        
        return HttpResponseForbidden("Você não tem permissão para acessar esta página."
                                        " Contate o administrador do sistema.")
    
class EmitirParecerPedInfo(LoginRequiredMixin, FormView):

    form_class = ParecerPedInfoForm
    template_name = 'lai_app/emissao_parecer.html'
    success_url = reverse_lazy('ped_infos_parecer')

    def dispatch(self, request, *args, **kwargs):

        ped_info = PedidoInformacao.objects.get(pk=self.kwargs['pk'])
        usuario = request.user
                
        if ( ped_info.situacao == 'EP' and 
            hasattr(usuario, 'funcionario') and
            usuario.funcionario.emite_parecer):

            return super().dispatch(request, *args, **kwargs)
        
        else:
            
            return HttpResponseForbidden("Você não tem permissão para acessar esta página."
                                        " Contate o administrador do sistema.")              
        
    def form_valid(self, form):
        
        ped_info = form.save(commit=False)
        ped_info.func_parecer = self.request.user.funcionario
        ped_info.data_parecer = dt.now()
        ped_info.situacao = 'DR' 

        ped_info.save()

        return super(EmitirParecerPedInfo, self).form_valid(form)

    def get_context_data(self, **kwargs):
        # Adiciona o objeto ao contexto para exibir no template
        context = super().get_context_data(**kwargs)
        context['ped_info'] = PedidoInformacao.objects.get(pk=self.kwargs['pk'])
        
        return context

    def get_form_kwargs(self):
        # Adiciona o objeto ao form para ser validado
        kwargs = super().get_form_kwargs()
        kwargs['instance'] = PedidoInformacao.objects.get(pk=self.kwargs['pk'])
        
        return kwargs

class FornecimentoInformacao(LoginRequiredMixin, FormView):

    form_class = FornecInfoForm
    template_name = 'lai_app/fornec_info.html'
    success_url = reverse_lazy('ped_infos_fornecimento')

    def dispatch(self, request, *args, **kwargs):

        ped_info = PedidoInformacao.objects.get(pk=self.kwargs['pk'])
        usuario = request.user
        
        if ( ped_info.situacao == 'BI' and 
            hasattr(usuario, 'funcionario') and
            usuario.funcionario.lotacao == ped_info.setor_info):

            return super().dispatch(request, *args, **kwargs)
        
        else:
            
            return HttpResponseForbidden("Você não tem permissão para acessar esta página."
                                        " Contate o administrador do sistema.")              
        
    def form_valid(self, form):
        
        ped_info = form.save(commit=False)
        ped_info.func_fornec = self.request.user.funcionario
        ped_info.data_fornec = dt.now()
        ped_info.situacao = 'EP' 

        ped_info.save()

        return super(FornecimentoInformacao, self).form_valid(form)

    def get_context_data(self, **kwargs):
        # Adiciona o objeto ao contexto para exibir no template
        context = super().get_context_data(**kwargs)
        context['ped_info'] = PedidoInformacao.objects.get(pk=self.kwargs['pk'])
        
        return context

    def get_form_kwargs(self):
        # Adiciona o objeto ao form para ser validado
        kwargs = super().get_form_kwargs()
        kwargs['instance'] = PedidoInformacao.objects.get(pk=self.kwargs['pk'])
        
        return kwargs

class InterporRecursoPrimeiraInst(LoginRequiredMixin, FormView):

    form_class = RecursoPrimInstForm
    template_name = 'lai_app/interpor_recurso_1.html'

    def dispatch(self, request, *args, **kwargs):

        ped_info = PedidoInformacao.objects.get(pk=self.kwargs['pk'])
        usuario = request.user
                
        if (ped_info.oportunidade_recurso_1 and 
            hasattr(usuario, 'cidadao') and
            ped_info.requerente == usuario.cidadao):
            
            return super().dispatch(request, *args, **kwargs)
        
        else:
            
            return HttpResponseForbidden("Você não tem permissão para acessar esta página."
                                        " Contate o administrador do sistema.")              
        
    def form_valid(self, form):
        
        ped_info = form.save(commit=False)
        ped_info.data_recurso_1 = dt.now()
        ped_info.situacao = 'AR' 

        ped_info.save()

        return redirect('detalhes_ped_info', pk=ped_info.pk)

    def get_context_data(self, **kwargs):
        # Adiciona o objeto ao contexto para exibir no template
        context = super().get_context_data(**kwargs)
        context['ped_info'] = PedidoInformacao.objects.get(pk=self.kwargs['pk'])
        
        return context

    def get_form_kwargs(self):
        # Adiciona o objeto ao form para ser validado
        kwargs = super().get_form_kwargs()
        kwargs['instance'] = PedidoInformacao.objects.get(pk=self.kwargs['pk'])
        
        return kwargs

class InterporRecursoSegundaInst(LoginRequiredMixin, FormView):

    form_class = RecursoSegInstForm
    template_name = 'lai_app/interpor_recurso_2.html'

    def dispatch(self, request, *args, **kwargs):

        ped_info = PedidoInformacao.objects.get(pk=self.kwargs['pk'])
        usuario = request.user
                
        if (ped_info.oportunidade_recurso_2 and 
            hasattr(usuario, 'cidadao') and
            ped_info.requerente == usuario.cidadao):
            
            return super().dispatch(request, *args, **kwargs)
        
        else:
            
            return HttpResponseForbidden("Você não tem permissão para acessar esta página."
                                        " Contate o administrador do sistema.")              
        
    def form_valid(self, form):
        
        ped_info = form.save(commit=False)
        ped_info.data_recurso_2 = dt.now()
        ped_info.situacao = 'AF' 

        ped_info.save()

        return redirect('detalhes_ped_info', pk=ped_info.pk)

    def get_context_data(self, **kwargs):
        # Adiciona o objeto ao contexto para exibir no template
        context = super().get_context_data(**kwargs)
        context['ped_info'] = PedidoInformacao.objects.get(pk=self.kwargs['pk'])
        
        return context

    def get_form_kwargs(self):
        # Adiciona o objeto ao form para ser validado
        kwargs = super().get_form_kwargs()
        kwargs['instance'] = PedidoInformacao.objects.get(pk=self.kwargs['pk'])
        
        return kwargs

class RequererInformacao(LoginRequiredMixin, FormView):

    form_class = ReqInformacaoForm
    template_name = 'lai_app/req_informacao.html'

    def dispatch(self, request, *args, **kwargs):

        if hasattr(request.user, 'cidadao') == False:
            return HttpResponseForbidden("Você não tem permissão para acessar esta página."
                                        " Contate o administrador do sistema.")        
        
        return super().dispatch(request, *args, **kwargs)

    def form_valid(self, form):
        
        req_informacao = form.save(commit=False)
        cidadao = self.request.user.cidadao
        req_informacao.requerente = cidadao

        req_informacao.save()
        return redirect('detalhes_ped_info', pk=req_informacao.pk)

class RespostaInicialPedInfo(LoginRequiredMixin, FormView):

    form_class = RespostaPedInfoForm
    template_name = 'lai_app/resposta_inicial.html'
    success_url = reverse_lazy('ped_infos_resposta')

    def dispatch(self, request, *args, **kwargs):

        ped_info = PedidoInformacao.objects.get(pk=self.kwargs['pk'])
        usuario = request.user
                
        if (ped_info.situacao == 'DR' and 
            hasattr(usuario, 'funcionario') and
            usuario.funcionario.responde_ped_info):

            return super().dispatch(request, *args, **kwargs)
        
        else:
            
            return HttpResponseForbidden("Você não tem permissão para acessar esta página."
                                        " Contate o administrador do sistema.")              
        
    def form_valid(self, form):
        
        ped_info = form.save(commit=False)

        if ped_info.resp_inicial==False:

            justificativa = ped_info.just_resp_inicial
            
            if not justificativa or justificativa.strip() == "":
                form.add_error(None, "A justificativa é obrigatória para indeferimento!")
                return super(RespostaInicialPedInfo, self).form_invalid(form)
        
        ped_info.func_resp_inicial = self.request.user.funcionario
        ped_info.data_resp_inicial = dt.now()
        ped_info.situacao = 'PR'

        ped_info.save()

        return super(RespostaInicialPedInfo, self).form_valid(form)

    def get_context_data(self, **kwargs):
        # Adiciona o objeto ao contexto para exibir no template
        context = super().get_context_data(**kwargs)
        context['ped_info'] = PedidoInformacao.objects.get(pk=self.kwargs['pk'])
        
        return context

    def get_form_kwargs(self):
        # Adiciona o objeto ao form para ser validado
        kwargs = super().get_form_kwargs()
        kwargs['instance'] = PedidoInformacao.objects.get(pk=self.kwargs['pk'])
        
        return kwargs

class RespostaRecursoPrimeiraInst(LoginRequiredMixin, FormView):

    form_class = RespostaRecPrimInstForm
    template_name = 'lai_app/resp_recurso_1.html'
    success_url = reverse_lazy('ped_infos_resp_rec_1')

    def dispatch(self, request, *args, **kwargs):

        ped_info = PedidoInformacao.objects.get(pk=self.kwargs['pk'])
        usuario = request.user
                
        if (ped_info.situacao == 'AR' and 
            hasattr(usuario, 'funcionario') and
            usuario.funcionario.responde_recurso_1):

            return super().dispatch(request, *args, **kwargs)
        
        else:
            
            return HttpResponseForbidden("Você não tem permissão para acessar esta página."
                                        " Contate o administrador do sistema.")              
        
    def form_valid(self, form):
        
        ped_info = form.save(commit=False)

        if ped_info.resp_recurso_1==False:

            justificativa = ped_info.just_resp_recurso_1
            
            if not justificativa or justificativa.strip() == "":
                form.add_error(None, "A justificativa é obrigatória para indeferimento!")
                return super(RespostaRecursoPrimeiraInst, self).form_invalid(form)
        
        ped_info.func_resp_recurso_1 = self.request.user.funcionario
        ped_info.data_resp_recurso_1 = dt.now()
        ped_info.situacao = 'RR'

        ped_info.save()

        return super(RespostaRecursoPrimeiraInst, self).form_valid(form)

    def get_context_data(self, **kwargs):
        # Adiciona o objeto ao contexto para exibir no template
        context = super().get_context_data(**kwargs)
        context['ped_info'] = PedidoInformacao.objects.get(pk=self.kwargs['pk'])
        
        return context

    def get_form_kwargs(self):
        # Adiciona o objeto ao form para ser validado
        kwargs = super().get_form_kwargs()
        kwargs['instance'] = PedidoInformacao.objects.get(pk=self.kwargs['pk'])
        
        return kwargs

class RespostaRecursoSegundaInst(LoginRequiredMixin, FormView):

    form_class = RespostaRecSegInstForm
    template_name = 'lai_app/resp_recurso_2.html'
    success_url = reverse_lazy('ped_infos_resp_rec_2')

    def dispatch(self, request, *args, **kwargs):

        ped_info = PedidoInformacao.objects.get(pk=self.kwargs['pk'])
        usuario = request.user
                
        if (ped_info.situacao == 'AF' and 
            hasattr(usuario, 'funcionario') and
            usuario.funcionario.responde_recurso_2):

            return super().dispatch(request, *args, **kwargs)
        
        else:
            
            return HttpResponseForbidden("Você não tem permissão para acessar esta página."
                                        " Contate o administrador do sistema.")              
        
    def form_valid(self, form):
        
        ped_info = form.save(commit=False)

        if ped_info.resp_recurso_2==False:

            justificativa = ped_info.just_resp_recurso_2
            
            if not justificativa or justificativa.strip() == "":
                form.add_error(None, "A justificativa é obrigatória para indeferimento!")
                return super(RespostaRecursoSegundaInst, self).form_invalid(form)
        
        ped_info.func_resp_recurso_2 = self.request.user.funcionario
        ped_info.data_resp_recurso_2 = dt.now()
        ped_info.situacao = 'RF'

        ped_info.save()

        return super(RespostaRecursoSegundaInst, self).form_valid(form)

    def get_context_data(self, **kwargs):
        # Adiciona o objeto ao contexto para exibir no template
        context = super().get_context_data(**kwargs)
        context['ped_info'] = PedidoInformacao.objects.get(pk=self.kwargs['pk'])
        
        return context

    def get_form_kwargs(self):
        # Adiciona o objeto ao form para ser validado
        kwargs = super().get_form_kwargs()
        kwargs['instance'] = PedidoInformacao.objects.get(pk=self.kwargs['pk'])
        
        return kwargs