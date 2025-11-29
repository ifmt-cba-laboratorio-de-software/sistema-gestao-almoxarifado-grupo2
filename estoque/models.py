from decimal import Decimal

from django.contrib.auth.models import AbstractUser
from django.core.validators import MinValueValidator
from django.db import models
from django.db.models import Sum
from django.db.models.functions import Coalesce
from django.utils import timezone


class Usuario(AbstractUser):
    """Usuários da aplicação alinhados ao DER."""

    class Perfil(models.TextChoices):
        ADMIN = "ADMIN", "Administrador"
        OPERADOR = "OPERADOR", "Operador"
        VISUALIZADOR = "VISUALIZADOR", "Visualizador"

    nome = models.CharField(max_length=100)
    perfil = models.CharField(max_length=20, choices=Perfil.choices, default=Perfil.OPERADOR)
    status = models.CharField(
        max_length=20,
        default="ATIVO",
        choices=(("ATIVO", "Ativo"), ("INATIVO", "Inativo")),
    )
    # MELHORIA: mantemos e-mails únicos para simplificar autenticação/contato
    email = models.EmailField(unique=True, max_length=80)

    def __str__(self) -> str:
        return f"{self.nome} ({self.get_perfil_display()})"


class Fornecedor(models.Model):
    nome = models.CharField(max_length=100)
    cnpj = models.CharField(max_length=20, blank=True, null=True)
    contato = models.CharField(max_length=100, blank=True, null=True)

    class Meta:
        ordering = ["nome"]

    def __str__(self) -> str:
        return self.nome


class Item(models.Model):
    codigo = models.CharField(max_length=50, unique=True)
    descricao = models.CharField(max_length=100)
    unidade_medida = models.CharField(max_length=20)
    valor_unitario = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        validators=[MinValueValidator(Decimal("0.00"))],
    )
    fornecedor = models.ForeignKey(
        Fornecedor, on_delete=models.SET_NULL, null=True, blank=True, related_name="itens"
    )
    estoque_minimo = models.PositiveIntegerField(default=0)
    estoque_maximo = models.PositiveIntegerField(default=0)
    ativo = models.BooleanField(default=True)
    criado_em = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["descricao"]

    def __str__(self) -> str:
        return self.descricao

    @property
    def estoque_total(self) -> int:
        """Total disponível considerando todos os estoques."""
        return (
            self.estoques.aggregate(total=Coalesce(Sum("qtde"), 0)).get("total")
            or 0
        )


class Estoque(models.Model):
    localizacao = models.CharField(max_length=120)
    qtde_atual = models.PositiveIntegerField(
        default=0, validators=[MinValueValidator(0)]
    )
    nivel_minimo = models.PositiveIntegerField(default=0, validators=[MinValueValidator(0)])
    criado_em = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["localizacao"]

    def __str__(self) -> str:
        return self.localizacao

    def atualizar_totais(self) -> None:
        """Recalcula quantidade total com base em ItemEstoque."""
        total = self.itens.aggregate(total=Coalesce(Sum("qtde"), 0)).get("total") or 0
        self.qtde_atual = total
        self.save(update_fields=["qtde_atual"])


class ItemEstoque(models.Model):
    estoque = models.ForeignKey(
        Estoque, related_name="itens", on_delete=models.CASCADE
    )
    item = models.ForeignKey(
        Item, related_name="estoques", on_delete=models.CASCADE
    )
    qtde = models.PositiveIntegerField(default=0, validators=[MinValueValidator(0)])

    class Meta:
        unique_together = ("estoque", "item")
        verbose_name = "Item no Estoque"
        verbose_name_plural = "Itens no Estoque"

    def __str__(self) -> str:
        return f"{self.item} em {self.estoque} ({self.qtde})"

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        # MELHORIA: sincroniza qtde_atual do Estoque sempre que o vínculo é alterado
        self.estoque.atualizar_totais()

    def delete(self, *args, **kwargs):
        estoque = self.estoque
        super().delete(*args, **kwargs)
        estoque.atualizar_totais()


class Inventario(models.Model):
    data_inventario = models.DateField(default=timezone.now)
    usuario = models.ForeignKey(
        Usuario, on_delete=models.PROTECT, related_name="inventarios"
    )
    observacao = models.TextField(blank=True)

    class Meta:
        ordering = ["-data_inventario"]

    def __str__(self) -> str:
        return f"Inventário {self.data_inventario:%d/%m/%Y}"


class InventarioItem(models.Model):
    inventario = models.ForeignKey(
        Inventario, related_name="itens", on_delete=models.CASCADE
    )
    item = models.ForeignKey(
        Item, related_name="inventarios", on_delete=models.PROTECT
    )
    qtde_contada = models.PositiveIntegerField(
        validators=[MinValueValidator(0)], help_text="Quantidade contada no inventário"
    )

    class Meta:
        unique_together = ("inventario", "item")
        verbose_name = "Item de Inventário"
        verbose_name_plural = "Itens de Inventário"

    def __str__(self) -> str:
        return f"{self.item} - {self.qtde_contada} un"


class Movimentacao(models.Model):
    class Tipo(models.TextChoices):
        ENTRADA = "ENTRADA", "Entrada"
        SAIDA = "SAIDA", "Saída"
        AJUSTE = "AJUSTE", "Ajuste"

    tipo_movimentacao = models.CharField(max_length=20, choices=Tipo.choices)
    observacao = models.CharField(max_length=100, blank=True)
    data_movimentacao = models.DateTimeField(default=timezone.now)
    quantidade = models.PositiveIntegerField(
        validators=[MinValueValidator(1)],
        help_text="Quantidade movimentada (sempre positiva)",
    )
    item = models.ForeignKey(
        Item, related_name="movimentacoes", on_delete=models.PROTECT
    )
    estoque = models.ForeignKey(
        Estoque, related_name="movimentacoes", on_delete=models.PROTECT
    )
    usuario = models.ForeignKey(
        Usuario, related_name="movimentacoes", on_delete=models.PROTECT
    )

    class Meta:
        ordering = ["-data_movimentacao"]

    def __str__(self) -> str:
        return f"{self.get_tipo_movimentacao_display()} - {self.item} ({self.quantidade})"

    @property
    def valor_movimentado(self) -> Decimal:
        """Valor total movimentado considerando o valor unitário."""
        sinal = Decimal("1") if self.tipo_movimentacao != self.Tipo.SAIDA else Decimal("-1")
        return (self.item.valor_unitario * self.quantidade) * sinal
