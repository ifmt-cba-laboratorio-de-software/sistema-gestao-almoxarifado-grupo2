from django.core.exceptions import ValidationError
from django.db import transaction
from django.db.models import Sum
from django.db.models.functions import Coalesce

from .models import ItemEstoque, Movimentacao


def registrar_movimentacao(*, usuario, item, estoque, tipo_movimentacao, quantidade, observacao=""):
    """
    Registra movimentação e atualiza o saldo do ItemEstoque de forma atômica.
    Levanta ValidationError se a operação levar a saldo negativo.
    """
    with transaction.atomic():
        item_estoque, _ = (
            ItemEstoque.objects.select_for_update()
            .get_or_create(estoque=estoque, item=item, defaults={"qtde": 0})
        )

        saldo_atual = item_estoque.qtde
        if tipo_movimentacao == Movimentacao.Tipo.SAIDA and quantidade > saldo_atual:
            raise ValidationError("A saída deixaria o estoque negativo.")

        if tipo_movimentacao in (Movimentacao.Tipo.ENTRADA, Movimentacao.Tipo.AJUSTE):
            novo_saldo = saldo_atual + quantidade
        else:
            novo_saldo = saldo_atual - quantidade

        item_estoque.qtde = novo_saldo
        item_estoque.save()

        movimento = Movimentacao.objects.create(
            item=item,
            estoque=estoque,
            tipo_movimentacao=tipo_movimentacao,
            quantidade=quantidade,
            observacao=observacao,
            usuario=usuario,
        )

        # MELHORIA: sincroniza o campo qtde_atual do estoque usando o vínculo ItemEstoque
        total_estoque = (
            ItemEstoque.objects.filter(estoque=estoque)
            .aggregate(total=Coalesce(Sum("qtde"), 0))
            .get("total")
            or 0
        )
        estoque.qtde_atual = total_estoque
        estoque.save(update_fields=["qtde_atual"])

        return movimento
