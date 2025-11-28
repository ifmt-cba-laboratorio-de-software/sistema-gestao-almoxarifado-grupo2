
﻿from django.urls import path


from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('item/novo/', views.item_create, name='item_create'),
    path('item/<int:pk>/editar/', views.item_edit, name='item_edit'),
    path('item/<int:pk>/excluir/', views.item_delete, name='item_delete'),
    path('item/<int:pk>/', views.item_detail, name='item_detail'),

    path('movimentacao/', views.movimentacao_list, name='movimentacao_list'),
    path('movimentacao/novo/', views.movimentacao_create, name='movimentacao_create'),
    path('inventario/periodico/', views.relatorio_inventario_periodico, name='relatorio_inventario_periodico'),

    path('movimentacao/novo/', views.movimentacao_create, name='movimentacao_create'),
    

]
