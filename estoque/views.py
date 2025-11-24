from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required, permission_required
from django.contrib import messages
from .models import Item, Movimentacao
from .forms import ItemForm, MovimentacaoForm
from django.core.paginator import Paginator
from django.contrib.auth import logout


@login_required
def index(request):
    items = Item.objects.all().order_by('descricao')
    paginator = Paginator(items, 20)
    page = request.GET.get('page')
    items = paginator.get_page(page)
    return render(request, 'estoque/item_list.html', {'items': items})

@login_required
@permission_required('estoque.add_item', raise_exception=True)
def item_create(request):
    if request.method == 'POST':
        form = ItemForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Item criado com sucesso.')
            return redirect('index')
    else:
        form = ItemForm()
    return render(request, 'estoque/item_form.html', {'form': form})

@login_required
@permission_required('estoque.change_item', raise_exception=True)
def item_edit(request, pk):
    item = get_object_or_404(Item, pk=pk)
    if request.method == 'POST':
        form = ItemForm(request.POST, instance=item)
        if form.is_valid():
            form.save()
            messages.success(request, 'Item atualizado com sucesso.')
            return redirect('index')
    else:
        form = ItemForm(instance=item)
    return render(request, 'estoque/item_form.html', {'form': form, 'item': item})

@login_required
@permission_required('estoque.delete_item', raise_exception=True)
def item_delete(request, pk):
    item = get_object_or_404(Item, pk=pk)
    if request.method == 'POST':
        item.delete()
        messages.success(request, 'Item removido.')
    else:
        messages.error(request, 'Acao invalida para exclusao.')
    return redirect('index')

@login_required
@permission_required('estoque.add_movimentacao', raise_exception=True)
def movimentacao_create(request):
    if request.method == 'POST':
        form = MovimentacaoForm(request.POST)
        if form.is_valid():
            mov = form.save(commit=False)
            mov.usuario = request.user
            mov.save()
            messages.success(request, 'Movimentacao registrada.')
            return redirect('movimentacao_list')
    else:
        form = MovimentacaoForm()
    return render(request, 'estoque/movimentacao_form.html', {'form': form})

@login_required
def movimentacao_list(request):
    movimentos = Movimentacao.objects.select_related('item', 'usuario').order_by('-data')
    paginator = Paginator(movimentos, 20)
    page = request.GET.get('page')
    movimentos_page = paginator.get_page(page)
    return render(request, 'estoque/movimentacao_list.html', {'movimentos': movimentos_page})

@login_required
def item_detail(request, pk):
    item = get_object_or_404(Item, pk=pk)
    movimentos = Movimentacao.objects.filter(item=item).order_by('-data')[:50]
    return render(request, 'estoque/item_detail.html', {'item': item, 'movimentos': movimentos})

@login_required
def logout_view(request):
    logout(request)
    return redirect('login')
