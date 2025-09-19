from django.test import TestCase
from datetime import datetime, timedelta
from .models import PedidoInformacao, Cidadao, Numerador
from .forms import CidadaoForm

# Testa o cadastro de um cidadão
class FormularioCidadaoTeste(TestCase):
    def test_form_valido(self):
        form_data = {
            'nome': 'João Silva',
            'num_doc_id': '123456789',
            'cep': '12345678',
            'logradouro': 'Rua A',
            'numero': '123',
            'bairro': 'Centro',
            'cidade': 'São Paulo',
            'estado': 'SP',
            'username': 'joaosilva',
            'email': 'joao@silva.com',
            'password': 'senhaSegura123',
            'password_confirm': 'senhaSegura123'
        }
        form = CidadaoForm(data=form_data)
        self.assertTrue(form.is_valid())

    def test_form_invalido(self):
        form_data = {
            'nome': '',
            'num_doc_id': '123456789',
        }
        form = CidadaoForm(data=form_data)
        self.assertFalse(form.is_valid())

# Testa se pedidos recem protocolados podem ser objeto de interposição de recursos
class ModeloPedidoInformacaoTeste(TestCase):
    
    def setUp(self):
        self.cidadao = Cidadao.objects.create(nome="João Silva", 
                                              num_doc_id="123456789",
                                              cep="12345678",
                                              logradouro="Rua A",
                                                numero="100",
                                                complemento="Apto 101",
                                                bairro="Centro",
                                                cidade="Cidade X",
                                                estado="XX")
        self.pedido = PedidoInformacao.objects.create(
            num_registro=1,
            titulo="Teste de Pedido",
            descricao="Descrição do pedido",
            requerente=self.cidadao,
            data_pedido=datetime.now(),
            situacao='AI'
        )

    def test_oportunidade_recurso_1(self):
        self.assertFalse(self.pedido.oportunidade_recurso_1())
    
    def test_oportunidade_recurso_2(self):
        self.assertFalse(self.pedido.oportunidade_recurso_2())

# Testa o numerador de pedidos
class NumeradorTeste(TestCase):
    def test_numerar(self):
        numero1 = Numerador.numerar()
        numero2 = Numerador.numerar()
        self.assertEqual(numero1, 1)
        self.assertEqual(numero2, 2)
