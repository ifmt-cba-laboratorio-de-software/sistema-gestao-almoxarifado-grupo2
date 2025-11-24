from django.db import models
from django.contrib.auth.models import User

class Fornecedor(models.Model):
    nome = models.CharField(max_length=100)
    cnpj = models.CharField(max_length=20, blank=True, null=True)
    contato = models.CharField(max_length=100, blank=True, null=True)

    def __str__(self):
        return self.nome

class Item(models.Model):
    codigo = models.CharField(max_length=20, unique=True)
    descricao = models.CharField(max_length=150)
    unidade_medida = models.CharField(max_length=20)
    valor_unitario = models.DecimalField(max_digits=10, decimal_places=2)
    fornecedor = models.ForeignKey(Fornecedor, on_delete=models.SET_NULL, null=True, blank=True)
    estoque_minimo = models.IntegerField(default=0)
    estoque_maximo = models.IntegerField(default=0)
    quantidade_atual = models.IntegerField(default=0)

    def __str__(self):
        return f"{self.codigo} - {self.descricao}"

class Movimentacao(models.Model):
    TIPO_CHOICES = [
        ('ENTRADA', 'Entrada'),
        ('SAIDA', 'Saída'),
        ('RETIRADA', 'Retirada Temporária'),
        ('DEVOLUCAO', 'Devolução'),
    ]
    item = models.ForeignKey(Item, on_delete=models.CASCADE)
    tipo = models.CharField(max_length=15, choices=TIPO_CHOICES)
    quantidade = models.IntegerField()
    data = models.DateTimeField(auto_now_add=True)
    usuario = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    data_devolucao_prevista = models.DateField(null=True, blank=True)

    def save(self, *args, **kwargs):
        # Salva movimentação e atualiza estoque do item
        super().save(*args, **kwargs)
        if self.tipo == 'ENTRADA' or self.tipo == 'DEVOLUCAO':
            self.item.quantidade_atual += self.quantidade
        elif self.tipo in ('SAIDA', 'RETIRADA'):
            self.item.quantidade_atual -= self.quantidade
            if self.item.quantidade_atual < 0:
                self.item.quantidade_atual = 0
        self.item.save()

    def __str__(self):
        return f"{self.tipo} - {self.item.descricao} ({self.quantidade})"
