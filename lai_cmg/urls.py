"""
URL configuration for lai_cmg project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.conf import settings
from django.conf.urls.static import static
from django.urls import include, path

from lai_app import views

urlpatterns = [
    path('', views.MenuView.as_view(), name='menu'),
    path('ped-info/analisar/<int:pk>/', views.AnaliseInicialPedInfo.as_view(), name='analisar_ped_info'),
    path('ped-info/fornecer/<int:pk>/', views.FornecimentoInformacao.as_view(), name='fornecer_ped_info'),
    path('ped-info/parecer/<int:pk>/', views.EmitirParecerPedInfo.as_view(), name='parecer_ped_info'),
    path('ped-info/resposta/<int:pk>/', views.RespostaInicialPedInfo.as_view(), name='resposta_ped_info'),
    path('ped-info/requerer/', views.RequererInformacao.as_view(), name='req_info'),
    path('ped-info/<int:pk>/', views.DetalhesPedInfo.as_view(), name='detalhes_ped_info'),
    path('ped-infos/analisar/', views.ConsultaPedInfosAnaliseInicial.as_view(), name='ped_infos_analise'),
    path('ped-infos/fornecer-info/', views.ConsultaPedInfosFornecInfo.as_view(), name='ped_infos_fornecimento'),
    path('ped-infos/parecer/', views.ConsultaPedInfosParecer.as_view(), name='ped_infos_parecer'),
    path('ped-infos/resposta/', views.ConsultaPedInfosRespInicial.as_view(), name='ped_infos_resposta'),

    path('registro-cidadao/', views.registrar_cidadao, name='registrar_cidadao'),
    path('accounts/', include('django.contrib.auth.urls')),
    path('admin/', admin.site.urls)

] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

admin.site.site_header = "Gerenciamento SisAIP"
admin.site.site_title = "SisAIP Admin"
admin.site.index_title = "Sistema de Acesso a Informações Públicas"