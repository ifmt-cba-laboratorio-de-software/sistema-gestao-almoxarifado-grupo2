from django import forms
from django.core.exceptions import ValidationError
from django.db.models import Sum
from django.db.models.functions import Coalesce

from .models import Estoque, Fornecedor, Inventario, InventarioItem, Item, Movimentacao


class ItemForm(forms.ModelForm):
    class Meta:
        model = Item
        fields = [
            "codigo",
            "descricao",
            "unidade_medida",
            "valor_unitario",
            "fornecedor",
            "estoque_minimo",
            "estoque_maximo",
            "ativo",
        ]
        widgets = {
            "codigo": forms.TextInput(attrs={"class": "form-control", "placeholder": "Código interno"}),
            "descricao": forms.TextInput(attrs={"class": "form-control", "placeholder": "Ex.: Parafuso 1/4"}),
            "unidade_medida": forms.TextInput(attrs={"class": "form-control", "placeholder": "un, cx, kg..."}),
            "valor_unitario": forms.NumberInput(attrs={"class": "form-control", "step": "0.01"}),
            "fornecedor": forms.Select(attrs={"class": "form-select"}),
            "estoque_minimo": forms.NumberInput(attrs={"class": "form-control", "min": 0}),
            "estoque_maximo": forms.NumberInput(attrs={"class": "form-control", "min": 0}),
            "ativo": forms.CheckboxInput(attrs={"class": "form-check-input"}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if "fornecedor" in self.fields:
            self.fields["fornecedor"].queryset = Fornecedor.objects.order_by("nome")

    def clean(self):
        cleaned = super().clean()
        minimo = cleaned.get("estoque_minimo") or 0
        maximo = cleaned.get("estoque_maximo") or 0
        if maximo and minimo and maximo < minimo:
            raise ValidationError("Estoque máximo não pode ser menor que o mínimo.")
        return cleaned


class MovimentacaoForm(forms.ModelForm):
    class Meta:
        model = Movimentacao
        fields = ["estoque", "item", "tipo_movimentacao", "quantidade", "observacao"]
        widgets = {
            "estoque": forms.Select(attrs={"class": "form-select"}),
            "item": forms.Select(attrs={"class": "form-select"}),
            "tipo_movimentacao": forms.Select(attrs={"class": "form-select"}),
            "quantidade": forms.NumberInput(attrs={"class": "form-control", "min": 1}),
            "observacao": forms.TextInput(
                attrs={
                    "class": "form-control",
                    "placeholder": "Observações (NF, ajuste, devolução...)",
                    "maxlength": 100,
                }
            ),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Trava o estoque em "Depósito Central"
        from .models import Estoque

        central = (
            Estoque.objects.filter(localizacao__iexact="Depósito Central").first()
            or Estoque.objects.first()
        )
        if central:
            self.fields["estoque"].queryset = Estoque.objects.filter(pk=central.pk)
            self.fields["estoque"].initial = central
            self.fields["estoque"].empty_label = None

    def clean_quantidade(self):
        quantidade = self.cleaned_data.get("quantidade") or 0
        if quantidade <= 0:
            raise ValidationError("A quantidade deve ser maior que zero.")
        return quantidade

    def clean(self):
        cleaned_data = super().clean()
        estoque = cleaned_data.get("estoque")
        item = cleaned_data.get("item")
        tipo = cleaned_data.get("tipo_movimentacao")
        quantidade = cleaned_data.get("quantidade") or 0

        if not estoque or not item or not tipo:
            return cleaned_data

        if tipo == Movimentacao.Tipo.SAIDA:
            saldo = (
                item.estoques.filter(estoque=estoque)
                .aggregate(total=Coalesce(Sum("qtde"), 0))
                .get("total")
                or 0
            )
            # MELHORIA: validação de regra de negócio para evitar estoque negativo
            if quantidade > saldo:
                raise ValidationError(
                    f"Saldo insuficiente. Disponível: {saldo} no estoque {estoque}."
                )

        return cleaned_data


class FornecedorForm(forms.ModelForm):
    class Meta:
        model = Fornecedor
        fields = ["nome", "cnpj", "contato"]
        widgets = {
            "nome": forms.TextInput(attrs={"class": "form-control", "placeholder": "Razão social / Nome"}),
            "cnpj": forms.TextInput(attrs={"class": "form-control", "placeholder": "CNPJ"}),
            "contato": forms.TextInput(attrs={"class": "form-control", "placeholder": "Telefone ou e-mail"}),
        }


class InventarioForm(forms.ModelForm):
    class Meta:
        model = Inventario
        fields = ["data_inventario", "observacao"]
        widgets = {
            "data_inventario": forms.DateInput(attrs={"type": "date", "class": "form-control"}),
            "observacao": forms.Textarea(attrs={"class": "form-control", "rows": 2, "placeholder": "Notas da contagem"}),
        }


class InventarioItemForm(forms.ModelForm):
    class Meta:
        model = InventarioItem
        fields = ["item", "qtde_contada"]
        widgets = {
            "item": forms.Select(attrs={"class": "form-select"}),
            "qtde_contada": forms.NumberInput(attrs={"class": "form-control", "min": 0}),
        }
