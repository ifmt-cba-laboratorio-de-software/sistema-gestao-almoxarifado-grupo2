from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from .models import Estoque, Fornecedor, Inventario, InventarioItem, Item, ItemEstoque, Movimentacao, Usuario


@admin.register(Usuario)
class UsuarioAdmin(UserAdmin):
    fieldsets = UserAdmin.fieldsets + (
        ("Perfil", {"fields": ("nome", "perfil", "status")}),
    )
    list_display = ("username", "nome", "email", "perfil", "is_active")
    list_filter = ("perfil", "is_active")
    search_fields = ("username", "nome", "email")


@admin.register(Fornecedor)
class FornecedorAdmin(admin.ModelAdmin):
    list_display = ("nome", "cnpj", "contato")
    search_fields = ("nome", "cnpj", "contato")


@admin.register(Item)
class ItemAdmin(admin.ModelAdmin):
    list_display = ("codigo", "descricao", "unidade_medida", "valor_unitario", "fornecedor", "estoque_minimo", "estoque_maximo", "ativo")
    search_fields = ("codigo", "descricao", "fornecedor__nome")
    list_filter = ("ativo", "fornecedor")


@admin.register(Estoque)
class EstoqueAdmin(admin.ModelAdmin):
    list_display = ("localizacao", "qtde_atual", "nivel_minimo")
    search_fields = ("localizacao",)


@admin.register(ItemEstoque)
class ItemEstoqueAdmin(admin.ModelAdmin):
    list_display = ("item", "estoque", "qtde")
    list_filter = ("estoque",)


class InventarioItemInline(admin.TabularInline):
    model = InventarioItem
    extra = 0


@admin.register(Inventario)
class InventarioAdmin(admin.ModelAdmin):
    list_display = ("data_inventario", "usuario")
    inlines = [InventarioItemInline]


@admin.register(Movimentacao)
class MovimentacaoAdmin(admin.ModelAdmin):
    list_display = ("item", "estoque", "tipo_movimentacao", "quantidade", "usuario", "data_movimentacao")
    list_filter = ("tipo_movimentacao", "estoque")
    search_fields = ("item__descricao", "observacao")
