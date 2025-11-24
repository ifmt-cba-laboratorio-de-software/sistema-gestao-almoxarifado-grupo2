from django import forms
from .models import Item, Movimentacao

class ItemForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if 'fornecedor' in self.fields:
            self.fields['fornecedor'].queryset = self.fields['fornecedor'].queryset.order_by('nome')

    class Meta:
        model = Item
        fields = '__all__'

class MovimentacaoForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if 'item' in self.fields:
            self.fields['item'].queryset = self.fields['item'].queryset.order_by('descricao')

    class Meta:
        model = Movimentacao
        fields = ['item', 'tipo', 'quantidade', 'data_devolucao_prevista']
        widgets = {
            'data_devolucao_prevista': forms.DateInput(
                attrs={'type': 'date', 'placeholder': 'dd/mm/aaaa'},
                format='%Y-%m-%d'
            )
        }
        input_formats = {
            'data_devolucao_prevista': ['%d/%m/%Y', '%Y-%m-%d']
        }
