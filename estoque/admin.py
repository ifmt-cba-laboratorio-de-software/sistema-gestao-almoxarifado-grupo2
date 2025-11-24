from django.contrib import admin
from .models import Fornecedor, Item, Movimentacao

@admin.register(Fornecedor)
class FornecedorAdmin(admin.ModelAdmin):
    list_display = ('nome', 'cnpj', 'contato')

@admin.register(Item)
class ItemAdmin(admin.ModelAdmin):
    list_display = ('codigo', 'descricao', 'quantidade_atual', 'estoque_minimo', 'estoque_maximo')
    search_fields = ('codigo', 'descricao')

@admin.register(Movimentacao)
class MovimentacaoAdmin(admin.ModelAdmin):
    list_display = ('item', 'tipo', 'quantidade', 'data', 'usuario')
    list_filter = ('tipo',)
