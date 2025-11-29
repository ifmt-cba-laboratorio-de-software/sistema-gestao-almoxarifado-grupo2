from decimal import Decimal

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth import logout
from django.core.exceptions import ValidationError
from django.db import models
from django.db.models import DecimalField, F, Sum, ExpressionWrapper
from django.db.models.functions import Coalesce
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, redirect, render

from .forms import FornecedorForm, InventarioForm, InventarioItemForm, ItemForm, MovimentacaoForm
from .models import Estoque, Fornecedor, Inventario, InventarioItem, Item, ItemEstoque, Movimentacao
from .services import registrar_movimentacao


@login_required
def dashboard(request):
    itens = Item.objects.annotate(total_qtde=Coalesce(Sum("estoques__qtde"), 0))
    total_itens = itens.count()
    valor_total = itens.annotate(
        total_valor=ExpressionWrapper(
            F("total_qtde") * F("valor_unitario"),
            output_field=DecimalField(max_digits=14, decimal_places=2),
        )
    ).aggregate(total=Coalesce(Sum("total_valor"), Decimal("0.00"))).get("total")

    criticos = (
        ItemEstoque.objects.select_related("item", "estoque")
        .filter(qtde__lt=F("estoque__nivel_minimo"))
        .order_by("estoque__localizacao", "item__descricao")
    )
    ultimas_movimentacoes = (
        Movimentacao.objects.select_related("item", "estoque", "usuario")
        .order_by("-data_movimentacao")[:8]
    )

    return render(
        request,
        "estoque/dashboard.html",
        {
            "total_itens": total_itens,
            "valor_total": valor_total,
            "criticos": criticos,
            "ultimas_movimentacoes": ultimas_movimentacoes,
        },
    )


@login_required
def item_list(request):
    query = request.GET.get("q", "").strip()
    fornecedor_id = request.GET.get("fornecedor")

    itens = Item.objects.annotate(total_qtde=Coalesce(Sum("estoques__qtde"), 0))
    if query:
        itens = itens.filter(
            models.Q(descricao__icontains=query)
            | models.Q(codigo__icontains=query)
            | models.Q(unidade_medida__icontains=query)
        )
    if fornecedor_id:
        itens = itens.filter(fornecedor_id=fornecedor_id)

    fornecedores = Fornecedor.objects.order_by("nome")

    return render(
        request,
        "estoque/item_list.html",
        {"itens": itens, "fornecedores": fornecedores, "q": query, "fornecedor_id": fornecedor_id},
    )


@login_required
def item_create(request):
    form = ItemForm(request.POST or None)
    if request.method == "POST" and form.is_valid():
        form.save()
        messages.success(request, "Item criado com sucesso.")
        return redirect("item_list")
    return render(request, "estoque/item_form.html", {"form": form})


@login_required
def item_edit(request, pk):
    item = get_object_or_404(Item, pk=pk)
    form = ItemForm(request.POST or None, instance=item)
    if request.method == "POST" and form.is_valid():
        form.save()
        messages.success(request, "Item atualizado com sucesso.")
        return redirect("item_list")
    return render(request, "estoque/item_form.html", {"form": form, "item": item})


@login_required
def movimentacao_list(request):
    movimentacoes = (
        Movimentacao.objects.select_related("item", "estoque", "usuario")
        .order_by("-data_movimentacao")
    )
    return render(request, "estoque/movimentacao_list.html", {"movimentacoes": movimentacoes})


@login_required
def movimentacao_create(request):
    initial = {}
    # Trava estoque em Depósito Central (ou primeiro disponível)
    central = (
        Estoque.objects.filter(localizacao__iexact="Depósito Central").first()
        or Estoque.objects.first()
    )
    if central:
        initial["estoque"] = central
    if request.GET.get("tipo"):
        initial["tipo_movimentacao"] = request.GET.get("tipo")

    form = MovimentacaoForm(request.POST or None, initial=initial)
    selected_item_id = ""
    if request.method == "POST":
        selected_item_id = request.POST.get("item", "")
    else:
        initial_item = form.initial.get("item")
        if initial_item:
            selected_item_id = getattr(initial_item, "id", initial_item)

    if request.method == "POST" and form.is_valid():
        try:
            registrar_movimentacao(
                usuario=request.user,
                **form.cleaned_data,
            )
        except ValidationError as exc:
            form.add_error(None, exc.message)
        else:
            # Guarda último estoque escolhido
            if central:
                request.session["last_estoque_id"] = central.id
            messages.success(request, "Movimentação registrada.")
            return redirect("movimentacao_list")

    return render(
        request,
        "estoque/movimentacao_form.html",
        {"form": form, "selected_item_id": selected_item_id, "central_estoque": central},
    )


@login_required
def logout_view(request):
    logout(request)
    return redirect("login")


@login_required
def inventario_list(request):
    inventarios = Inventario.objects.select_related("usuario").order_by("-data_inventario")
    return render(request, "estoque/inventario_list.html", {"inventarios": inventarios})


@login_required
def inventario_create(request):
    form = InventarioForm(request.POST or None)
    if request.method == "POST" and form.is_valid():
        inventario = form.save(commit=False)
        inventario.usuario = request.user
        inventario.save()
        messages.success(request, "Inventário criado. Registre as contagens.")
        return redirect("inventario_detail", pk=inventario.pk)
    return render(request, "estoque/inventario_form.html", {"form": form})


@login_required
def inventario_detail(request, pk):
    inventario = get_object_or_404(Inventario, pk=pk)
    form = InventarioItemForm(request.POST or None)
    itens = InventarioItem.objects.select_related("item").filter(inventario=inventario)
    estoques = Estoque.objects.order_by("localizacao")

    # Contagem rápida por código
    if request.method == "POST" and request.POST.get("codigo_lookup"):
        codigo = request.POST.get("codigo_lookup").strip()
        qtde_lookup = int(request.POST.get("qtde_lookup") or 0)
        try:
            item = Item.objects.get(codigo=codigo)
            inv_item, _ = InventarioItem.objects.get_or_create(inventario=inventario, item=item, defaults={"qtde_contada": 0})
            inv_item.qtde_contada = qtde_lookup
            inv_item.save()
            messages.success(request, f"Contagem registrada para {item.descricao}.")
        except Item.DoesNotExist:
            messages.error(request, "Item não encontrado para o código informado.")
        return redirect("inventario_detail", pk=pk)

    if request.method == "POST" and form.is_valid():
        inv_item = form.save(commit=False)
        inv_item.inventario = inventario
        inv_item.save()
        messages.success(request, "Contagem registrada no inventário.")
        return redirect("inventario_detail", pk=pk)

    return render(
        request,
        "estoque/inventario_detail.html",
        {"inventario": inventario, "form": form, "itens": itens, "estoques": estoques},
    )


@login_required
def inventario_encerrar(request, pk):
    inventario = get_object_or_404(Inventario, pk=pk)
    if request.method != "POST":
        return redirect("inventario_detail", pk=pk)
    estoque_id = request.POST.get("estoque_id")
    estoque = get_object_or_404(Estoque, pk=estoque_id) if estoque_id else None
    if not estoque:
        messages.error(request, "Selecione um estoque para aplicar os ajustes.")
        return redirect("inventario_detail", pk=pk)

    ajustes_criados = 0
    for inv_item in inventario.itens.select_related("item"):
        saldo = (
            ItemEstoque.objects.filter(item=inv_item.item, estoque=estoque)
            .aggregate(total=Coalesce(Sum("qtde"), 0))
            .get("total")
            or 0
        )
        diff = inv_item.qtde_contada - saldo
        if diff == 0:
            continue
        try:
            registrar_movimentacao(
                usuario=request.user,
                item=inv_item.item,
                estoque=estoque,
                tipo_movimentacao=Movimentacao.Tipo.AJUSTE if diff > 0 else Movimentacao.Tipo.SAIDA,
                quantidade=abs(diff),
                observacao=f"Ajuste inventário {inventario.id}",
            )
            ajustes_criados += 1
        except ValidationError as exc:
            messages.error(request, f"Erro ao ajustar {inv_item.item}: {exc.message}")
    if ajustes_criados:
        messages.success(request, f"Inventário encerrado com {ajustes_criados} ajustes.")
    else:
        messages.info(request, "Inventário encerrado sem ajustes necessários.")
    return redirect("inventario_detail", pk=pk)


# --- CRUD de Fornecedor ---
@login_required
def fornecedor_list(request):
    fornecedores = Fornecedor.objects.order_by("nome")
    return render(request, "estoque/fornecedor_list.html", {"fornecedores": fornecedores})


@login_required
def fornecedor_create(request):
    form = FornecedorForm(request.POST or None)
    if request.method == "POST" and form.is_valid():
        form.save()
        messages.success(request, "Fornecedor cadastrado com sucesso.")
        return redirect("fornecedor_list")
    return render(request, "estoque/fornecedor_form.html", {"form": form})


@login_required
def fornecedor_edit(request, pk):
    fornecedor = get_object_or_404(Fornecedor, pk=pk)
    form = FornecedorForm(request.POST or None, instance=fornecedor)
    if request.method == "POST" and form.is_valid():
        form.save()
        messages.success(request, "Fornecedor atualizado com sucesso.")
        return redirect("fornecedor_list")
    return render(request, "estoque/fornecedor_form.html", {"form": form, "fornecedor": fornecedor})


@login_required
def fornecedor_delete(request, pk):
    fornecedor = get_object_or_404(Fornecedor, pk=pk)
    if request.method == "POST":
        fornecedor.delete()
        messages.success(request, "Fornecedor removido.")
        return redirect("fornecedor_list")
    return render(request, "estoque/fornecedor_form.html", {"form": None, "fornecedor": fornecedor, "confirm_delete": True})


# --- APIs auxiliares para UX ---
@login_required
def api_item_search(request):
    """Busca rápida para autocomplete de itens."""
    q = request.GET.get("q", "").strip()
    itens = Item.objects.all()
    if q:
        itens = itens.filter(models.Q(descricao__icontains=q) | models.Q(codigo__icontains=q))
    itens = itens.order_by("descricao")[:15]
    data = [
        {
            "id": item.id,
            "text": f"{item.codigo} - {item.descricao}" if item.codigo else item.descricao,
        }
        for item in itens
    ]
    return JsonResponse({"results": data})


@login_required
def api_item_saldo(request):
    """Retorna saldo por item/estoque e min/máx configurados."""
    item_id = request.GET.get("item")
    estoque_id = request.GET.get("estoque")
    if not item_id or not estoque_id:
        return JsonResponse({"error": "Parâmetros faltando"}, status=400)

    try:
        item = Item.objects.get(pk=item_id)
        saldo = (
            item.estoques.filter(estoque_id=estoque_id)
            .aggregate(total=Coalesce(Sum("qtde"), 0))
            .get("total")
            or 0
        )
    except Item.DoesNotExist:
        return JsonResponse({"error": "Item não encontrado"}, status=404)

    return JsonResponse(
        {
            "saldo": saldo,
            "estoque_minimo": item.estoque_minimo,
            "estoque_maximo": item.estoque_maximo,
            "unidade_medida": item.unidade_medida,
        }
    )


@login_required
def api_fornecedor_create(request):
    """Cria fornecedor via AJAX."""
    if request.method != "POST":
        return JsonResponse({"error": "Método não permitido"}, status=405)
    form = FornecedorForm(request.POST)
    if form.is_valid():
        fornecedor = form.save()
        return JsonResponse({"id": fornecedor.id, "nome": fornecedor.nome})
    return JsonResponse({"errors": form.errors}, status=400)
