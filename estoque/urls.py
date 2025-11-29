from django.urls import path

from . import views

urlpatterns = [
    path("", views.dashboard, name="dashboard"),
    path("itens/", views.item_list, name="item_list"),
    path("itens/novo/", views.item_create, name="item_create"),
    path("itens/<int:pk>/editar/", views.item_edit, name="item_edit"),
    path("movimentacoes/", views.movimentacao_list, name="movimentacao_list"),
    path("movimentacoes/nova/", views.movimentacao_create, name="movimentacao_create"),
    path("inventarios/", views.inventario_list, name="inventario_list"),
    path("inventarios/novo/", views.inventario_create, name="inventario_create"),
    path("inventarios/<int:pk>/", views.inventario_detail, name="inventario_detail"),
    path("inventarios/<int:pk>/encerrar/", views.inventario_encerrar, name="inventario_encerrar"),
    path("fornecedores/", views.fornecedor_list, name="fornecedor_list"),
    path("fornecedores/novo/", views.fornecedor_create, name="fornecedor_create"),
    path("fornecedores/<int:pk>/editar/", views.fornecedor_edit, name="fornecedor_edit"),
    path("fornecedores/<int:pk>/excluir/", views.fornecedor_delete, name="fornecedor_delete"),
    # APIs
    path("api/item-search/", views.api_item_search, name="api_item_search"),
    path("api/item-saldo/", views.api_item_saldo, name="api_item_saldo"),
    path("api/fornecedor/", views.api_fornecedor_create, name="api_fornecedor_create"),
]
