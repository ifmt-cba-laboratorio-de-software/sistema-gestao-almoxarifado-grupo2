from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required, permission_required
from django.contrib import messages
from .models import Item, Movimentacao
from .forms import ItemForm, MovimentacaoForm
from django.core.paginator import Paginator
from django.contrib.auth import logout
from datetime import datetime, date
from decimal import Decimal
from django.db.models import Sum, F, ExpressionWrapper, DecimalField, Case, When
from django.utils import timezone

def get_historical_stock_value(end_date):
    """
    Calcula o valor total do estoque em uma data específica
    somando o valor de todas as ENTREDAS e subtraindo o valor de todas as SAÍDAS
    até essa data.
    """
    
    # Adiciona o fuso horário à data final
    if not isinstance(end_date, datetime):
        end_date = timezone.make_aware(datetime.combine(end_date, datetime.max.time()))

    # --- CORREÇÃO DO ERRO: Adicionar output_field em ExpressionWrapper ---
    
    # Define o custo negativo para as saídas (SAIDA, RETIRADA)
    CUSTO_NEGATIVO = ExpressionWrapper(
        F('quantidade') * F('item__valor_unitario') * Decimal('-1'),
        # Necessário para forçar o resultado da multiplicação a ser Decimal
        output_field=DecimalField() 
    )
    
    # Define o custo positivo para as entradas (ENTRADA, DEVOLUCAO)
    CUSTO_POSITIVO = ExpressionWrapper(
        F('quantidade') * F('item__valor_unitario'),
        # Necessário para forçar o resultado da multiplicação a ser Decimal
        output_field=DecimalField()
    )

    # Calcula a alteração líquida no valor do estoque até a data final
    stock_value = Movimentacao.objects.filter(
        data__lte=end_date
    ).select_related('item').annotate(
        # Cria o campo 'valor_movimentado'
        valor_movimentado=ExpressionWrapper(
            Case(
                # ENTRADA / DEVOLUCAO adiciona valor
                When(tipo__in=['ENTRADA', 'DEVOLUCAO'], 
                     then=CUSTO_POSITIVO),
                # SAIDA / RETIRADA reduz valor
                When(tipo__in=['SAIDA', 'RETIRADA'], 
                     then=CUSTO_NEGATIVO),
                # Garante que o Case inteiro retorne um Decimal
                default=Decimal('0.00'),
                output_field=DecimalField()
            ),
            output_field=DecimalField() # Garante que a anotação final é Decimal
        )
    ).aggregate(
        total_valor_estoque=Sum('valor_movimentado')
    )
    
    return stock_value.get('total_valor_estoque') or Decimal('0.00')


@login_required
@permission_required('estoque.view_movimentacao', raise_exception=True)
def relatorio_inventario_periodico(request):
    # --- 1. DEFINIÇÃO DO PERÍODO ---
    
    # Pega as datas do formulário (GET), ou usa a data de hoje/início do mês como padrão
    data_fim_default = date.today().strftime('%Y-%m-%d')
    data_inicio_default = date.today().replace(day=1).strftime('%Y-%m-%d') # Início do mês atual
    
    data_inicio_str = request.GET.get('data_inicio', data_inicio_default)
    data_fim_str = request.GET.get('data_fim', data_fim_default)
    
    try:
        data_inicio_date = datetime.strptime(data_inicio_str, '%Y-%m-%d').date()
        data_fim_date = datetime.strptime(data_fim_str, '%Y-%m-%d').date()
        
        # Cria objetos datetime com horário de início e fim do dia para consultas precisas
        data_inicio = timezone.make_aware(datetime.combine(data_inicio_date, datetime.min.time()))
        data_fim = timezone.make_aware(datetime.combine(data_fim_date, datetime.max.time()))

    except ValueError:
        messages.error(request, "Formato de data inválido. Use AAAA-MM-DD.")
        return render(request, 'estoque/relatorio_cmv.html', {})
        
    # --- 2. CÁLCULO DAS VARIÁVEIS CHAVE ---
    
    # A. Estoque Inicial (EI): Valor total do estoque no final do dia anterior a data_inicio
    valor_estoque_inicial = get_historical_stock_value(data_inicio)
    
    # B. Compras Líquidas (C): Valor de todas as ENTRADAS no período
    compras_no_periodo = Movimentacao.objects.filter(
        tipo='ENTRADA',
        data__range=(data_inicio, data_fim)
    ).select_related('item')
    
    valor_compras_liquidas = Decimal('0.00')
    for mov in compras_no_periodo:
        # Soma o valor total de cada entrada (Quantidade * Custo Unitário)
        valor_compras_liquidas += mov.quantidade * mov.item.valor_unitario
        
    # C. Estoque Disponível para Uso (EDU): EI + C
    valor_estoque_disponivel = valor_estoque_inicial + valor_compras_liquidas
    
    # D. Estoque Final (EF): Valor total do estoque no final do dia de data_fim
    valor_estoque_final_contado = get_historical_stock_value(data_fim)

    # E. Custo de Uso (Saídas): EDU - EF
    # Custo de Uso = Estoque Inicial + Compras - Estoque Final
    custo_uso = valor_estoque_disponivel - valor_estoque_final_contado
    
    # Filtra os itens com estoque final > 0 para detalhamento
    itens_detalhe = Item.objects.all().filter(quantidade_atual__gt=0).order_by('descricao')
    
    context = {
        'data_inicio': data_inicio_str,
        'data_fim': data_fim_str,
        'valor_estoque_inicial': valor_estoque_inicial,
        'valor_compras_liquidas': valor_compras_liquidas,
        'valor_estoque_disponivel': valor_estoque_disponivel,
        'valor_estoque_final_contado': valor_estoque_final_contado,
        'custo_uso': custo_uso, # Variável renomeada
        'itens': itens_detalhe
    }

    return render(request, 'estoque/relatorio_cmv.html', context)

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
