from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth.models import User

from .models import Cargo, Cidadao, Configuracao, Funcionario, Setor

class CargoAdmin(admin.ModelAdmin):
    list_display = ('nome', 'detalhes')
    search_fields = ('nome',)

class CidadaoAdmin(admin.ModelAdmin):
    list_display = ('nome', 'num_doc_id', 'credenciais')
    search_fields = ('nome', 'num_doc_id', 'credenciais__username', 'credenciais__email')
    readonly_fields = ('nome','num_doc_id','cep','logradouro','numero','complemento','bairro','cidade','estado','credenciais')

    def has_delete_permission(self, request, obj = None):
        return False
    
    def has_add_permission(self, request):
        return False
  
class ConfiguracaoAdmin(admin.ModelAdmin):

  def has_delete_permission(self, request, obj = None):
    return False
  
class FuncionarioAdmin(admin.ModelAdmin):
    list_display = ('nome', 'cargo', 'lotacao', 'credenciais')
    search_fields = ('nome', 'cargo__nome', 'lotacao__nome', 'credenciais__username', 'credenciais__email')

class SetorAdmin(admin.ModelAdmin):
    list_display = ('nome', 'detalhes')
    search_fields = ('nome', 'sigla')

admin.site.register(Cargo, CargoAdmin)
admin.site.register(Cidadao, CidadaoAdmin)
admin.site.register(Configuracao, ConfiguracaoAdmin)
admin.site.register(Funcionario, FuncionarioAdmin)
admin.site.register(Setor, SetorAdmin)