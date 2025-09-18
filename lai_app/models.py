from django.db import models, transaction
from django.contrib.auth.models import User
from django.core.cache import cache
from django.utils.timezone import now
from datetime import datetime as dt

class SingletonModel(models.Model):

    class Meta:
        abstract = True

    def set_cache(self):
        cache.get(self.__class__.__name__, self)

    def save(self, *args, **kwargs):
        self.pk = 1
        super(SingletonModel, self).save(*args, **kwargs)
        self.set_cache()
    
    def delete(self, *args, **kwargs):
        pass

    @classmethod
    def load(cls):
        if cache.get(cls.__name__) is None:
            obj, created = cls.objects.get_or_create(pk=1)
            if not created:
                obj.set_cache()
        return cache.get(cls.__name__)

class Cargo(models.Model):
    
    nome = models.CharField(max_length=50)
    detalhes = models.CharField(max_length=250, blank=True, null=True)
    ativo = models.BooleanField(default=True)

    def __str__(self):
        return self.nome

    class Meta:
        verbose_name = "Cargo"
        verbose_name_plural = "Cargos"

class Cidadao(models.Model):
    
    nome = models.CharField(max_length=100)
    num_doc_id = models.CharField(max_length=20, verbose_name="Documento de Identificação")
    cep = models.CharField(max_length=8, verbose_name="CEP")
    logradouro = models.CharField(max_length=100)
    numero = models.CharField(max_length=10, verbose_name="Número")
    complemento = models.CharField(max_length=50, blank=True, null=True)
    bairro = models.CharField(max_length=50)
    cidade = models.CharField(max_length=50)
    estado = models.CharField(max_length=2)
    credenciais = models.OneToOneField(User, on_delete=models.CASCADE, blank=True, null= True,
                                       verbose_name="Credenciais de Acesso")

    def __str__(self):
        return self.nome + " (" + self.num_doc_id + ")"

    class Meta:
        verbose_name = "Cidadão"
        verbose_name_plural = "Cidadãos"

class Configuracao(SingletonModel):
    
    setor_adm = models.ForeignKey('Setor', on_delete=models.PROTECT, blank=True, null=True,
                                    verbose_name="Setor Administrativo", related_name='setor_adm')
    setor_parecer = models.ForeignKey('Setor', on_delete=models.PROTECT, blank=True, null=True,
                                        verbose_name="Setor Emissor de Parecer", related_name='setor_parecer')
    setor_resposta = models.ForeignKey('Setor', on_delete=models.PROTECT, blank=True, null=True,
                                        verbose_name="Setor Emissor de Resposta", related_name='setor_resposta')
    setor_recurso_1 = models.ForeignKey('Setor', on_delete=models.PROTECT, blank=True, null=True,
                                        verbose_name="Setor do Responsável pelo Recurso em 1ª Instância", 
                                        related_name='setor_recurso_1')
    setor_recurso_2 = models.ForeignKey('Setor', on_delete=models.PROTECT, blank=True, null=True,
                                        verbose_name="Setor do Responsável pelo Recurso em 2ª Instância", 
                                        related_name='setor_recurso_2')

    def __str__(self):
        return "Configurações Globais"

    class Meta:
        verbose_name = "Configuração"
        verbose_name_plural = "Configurações"

class Funcionario(models.Model):
    
    nome = models.CharField(max_length=100)
    matricula = models.CharField(max_length=10, unique=True, verbose_name="matrícula")
    cargo = models.ForeignKey('Cargo', on_delete=models.PROTECT, verbose_name="Cargo")
    lotacao = models.ForeignKey('Setor', on_delete=models.PROTECT, verbose_name="Lotação")
    credenciais = models.OneToOneField(User, on_delete=models.CASCADE, blank=True, null= True,
                                       verbose_name="Credenciais de Acesso")
           
    def analisa_ped_info(self):

        if self.lotacao != Configuracao.objects.get(id=1).setor_adm:
            return False
        
        return True
    
    def emite_parecer(self):

        if self.lotacao != Configuracao.objects.get(id=1).setor_parecer:
            return False
        
        return True
    
    def responde_ped_info(self):

        if self.lotacao != Configuracao.objects.get(id=1).setor_resposta:
            return False
        
        return True
    
    def responde_recurso_1(self):

        if self.lotacao != Configuracao.objects.get(id=1).setor_recurso_1:
            return False
        
        return True
    
    def responde_recurso_2(self):

        if self.lotacao != Configuracao.objects.get(id=1).setor_recurso_2:
            return False
        
        return True

    def __str__(self):
        return self.nome + " (" + self.matricula + ")"

    class Meta:
        verbose_name = "Funcionário"
        verbose_name_plural = "Funcionários"

class Numerador(models.Model):
        
    exercicio_num = models.PositiveSmallIntegerField("exercício")
    ultimo_num = models.PositiveBigIntegerField("último número", default=0)

    @classmethod
    def numerar(cls):
        
        with transaction.atomic():

            exercicio = dt.now().year
            
            try:
                numeracao_exerc = cls.objects.select_for_update().get(exercicio_num = exercicio)
            except cls.DoesNotExist:          
                numeracao_exerc = Numerador(exercicio_num=exercicio)
            
            numeracao_exerc.ultimo_num += 1
            numeracao_exerc.save()
            return numeracao_exerc.ultimo_num

class PedidoInformacao(models.Model):

    SITUACOES = {
        "AI": "Análise Inicial",
        "BI": "Buscando Informações",
        "EP": "Elaborando Parecer",
        "DR": "Definindo Resposta",
        "PR": "Pedido Respondido",
        "AR": "Analisando Recurso",
        "RR": "Recurso Respondido",
        "AF": "Analisando Recurso Final",
        "RF": "Recurso Final Respondido"
    }

    situacao = models.CharField(max_length=2, choices=SITUACOES,
                                default='AI', verbose_name="Situação")

    # Campos da Criação do Pedido de Informação
    num_registro = models.PositiveIntegerField(unique_for_year=True, 
                                               verbose_name="Número de Registro")
    titulo = models.CharField(max_length=100, verbose_name="Título")
    descricao = models.TextField(verbose_name="Descrição")
    data_pedido = models.DateTimeField(auto_now_add=True, verbose_name="Data do Pedido")
    requerente = models.ForeignKey('Cidadao', on_delete=models.PROTECT, 
                                   related_name='cid_req', verbose_name="Requerente")

    # Campos do Setor Administrativo
    setor_info = models.ForeignKey('Setor', on_delete=models.PROTECT, 
                                    verbose_name="Setor Fornecedor da Informação", 
                                    blank=True, null=True)
    data_encam = models.DateTimeField(blank=True, null=True, 
                                  verbose_name="Data de Encaminhamento")
    func_adm = models.ForeignKey('Funcionario', on_delete=models.PROTECT, 
                                 verbose_name="Funcionário do Setor Administrativo", 
                                 blank=True, null=True, related_name='func_adm')
    
    # Campos do Setor Fornecedor da Informação
    arquivo_info = models.FileField(upload_to='documentos/', 
                                    verbose_name="Caminho do Arquivo", 
                                    blank=True, null=True)
    observacoes_forn = models.TextField(blank=True, null=True, verbose_name="Observações")
    data_fornec = models.DateTimeField(blank=True, null=True, 
                                      verbose_name="Data de Fornecimento da Informação")
    func_fornec = models.ForeignKey('Funcionario', on_delete=models.PROTECT, 
                                   verbose_name="Funcionário do Setor Fornecedor", 
                                   blank=True, null=True, related_name='func_fornec')
    
    # Campos do Setor Emissor do Parecer
    parecer = models.TextField(blank=True, null=True)
    data_parecer = models.DateTimeField(blank=True, null=True,
                                        verbose_name="Data do Parecer")
    func_parecer = models.ForeignKey('Funcionario', on_delete=models.PROTECT, 
                                    verbose_name="Funcionário do Setor Emissor do Parecer", 
                                    blank=True, null=True, related_name='func_parecer')

    # Campos do Setor de Resposta
    resp_inicial = models.BooleanField(default=False, # Se False significa "Indeferido", casos contrários "Deferido"
                                       verbose_name="Pedido Deferido?")
    just_resp_inicial = models.TextField(blank=True, null=True,
                                         verbose_name="Justificativa")
    data_resp_inicial = models.DateTimeField(blank=True, null=True,
                                            verbose_name="Data da Resposta Inicial")
    func_resp_inicial = models.ForeignKey('Funcionario', on_delete=models.PROTECT,
                                            verbose_name="Funcionário Emissor da Resposta Inicial", 
                                            blank=True, null=True, related_name='func_resp_inicial')

    # Campos do Recurso em 1ª Instância
    prazo_recurso_1 = models.DateTimeField(blank=True, null=True,
                                          verbose_name="Prazo para Recurso em 1ª Instância")
    recurso_1 = models.TextField(blank=True, null=True,
                                 verbose_name="Recurso em 1ª Instância")
    data_recurso_1 = models.DateTimeField(blank=True, null=True,
                                          verbose_name="Data do Recurso em 1ª Instância")

    #Campos da Resposta ao Recurso em 1ª Instância
    resp_recurso_1 = models.BooleanField(default=False, # Se False significa "Indeferido", casos contrários "Deferido"
                                       verbose_name="Resposta ao Recurso em 1ª Instância")
    just_resp_recurso_1 = models.TextField(blank=True, null=True,
                                         verbose_name="Justificativa da Resposta ao Recurso em 1ª Instância")
    data_resp_recurso_1 = models.DateTimeField(blank=True, null=True,
                                            verbose_name="Data da Resposta ao Recurso em 1ª Instância")
    func_resp_recurso_1 = models.ForeignKey('Funcionario', on_delete=models.PROTECT,
                                            verbose_name="Funcionário da Resposta ao Recurso em 1ª Instância", 
                                            blank=True, null=True, related_name='func_resp_recurso_1')
    
    # Campos do Recurso em 2ª Instância
    prazo_recurso_2 = models.DateTimeField(blank=True, null=True,
                                          verbose_name="Prazo para Recurso em 2ª Instância")
    recurso_2 = models.TextField(blank=True, null=True,
                                    verbose_name="Recurso em 2ª Instância")
    data_recurso_2 = models.DateTimeField(blank=True, null=True,
                                          verbose_name="Data do Recurso em 2ª Instância")
    
    #Campos da Resposta ao Recurso em 2ª Instância
    resp_recurso_2 = models.BooleanField(default=False, # Se False significa "Indeferido", casos contrários "Deferido"
                                       verbose_name="Resposta ao Recurso em 2ª Instância")
    just_resp_recurso_2 = models.TextField(blank=True, null=True,
                                            verbose_name="Justificativa da Resposta ao Recurso em 2ª Instância")
    data_resp_recurso_2 = models.DateTimeField(blank=True, null=True,
                                            verbose_name="Data da Resposta ao Recurso em 2ª Instância")
    func_resp_recurso_2 = models.ForeignKey('Funcionario', on_delete=models.PROTECT,
                                            verbose_name="Funcionário da Resposta ao Recurso em 2ª Instância", 
                                            blank=True, null=True, related_name='func_resp_recurso_2')

    def oportunidade_recurso_1(self):
        if (self.prazo_recurso_1 and 
            now() <= self.prazo_recurso_1 and
            self.situacao == 'PR'):
                return True
        return False
    
    def oportunidade_recurso_2(self):
        if (self.prazo_recurso_2 and 
            now() <= self.prazo_recurso_2 and
            self.situacao == 'RR'):
                return True
        return False
    
    def save(self, *args, **kwargs):
        
        if self.num_registro is None:                        
            self.num_registro = Numerador.numerar()

        super(PedidoInformacao, self).save(*args, **kwargs)

    def __str__(self):
        return f"{self.num_registro}/{self.data_pedido.year}"

    class Meta:
        verbose_name = "Pedido de Informação"
        verbose_name_plural = "Pedidos de Informação"

class Setor(models.Model):
    
    nome = models.CharField(max_length=50)
    sigla = models.CharField(max_length=10)
    detalhes = models.CharField(max_length=250, blank=True, null=True)
    ativo = models.BooleanField(default=True)

    def __str__(self):
        return self.nome

    class Meta:
        verbose_name = "Setor"
        verbose_name_plural = "Setores"
