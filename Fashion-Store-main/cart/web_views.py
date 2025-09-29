from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.shortcuts import redirect, render, get_object_or_404
from catalog.models import Product, ProductVariant
from .models import Cart, CartItem
from orders.models import Coupon
from decimal import Decimal
from django.db.models import Sum

MAX_ITEMS_IN_CART = 2

def _get_cart(user):
    cart, _ = Cart.objects.get_or_create(user=user)
    return cart

@login_required
def view_cart(request):
    cart = _get_cart(request.user)
    items = cart.items.select_related('variant','variant__product')
    subtotal = sum([i.subtotal for i in items], Decimal('0.00'))
    discount = Decimal('0.00')
    if cart.coupon_code:
        try:
            c = Coupon.objects.get(code__iexact=cart.coupon_code, active=True)
            discount = c.apply(subtotal)
        except Coupon.DoesNotExist:
            messages.error(request, "Invalid coupon")
    total = max(Decimal('0.00'), subtotal - discount)

    # fetch all addresses of logged-in user
    addresses = request.user.addresses.all()

    return render(
        request,
        'cart/cart.html',
        {
            'items': items,
            'totals': {'subtotal': subtotal, 'discount': discount, 'total': total},
            'addresses': addresses
        }
    )

@login_required
def add_to_cart(request, product_id):
    if request.method == 'POST':
        size = request.POST.get('size')
        color = request.POST.get('color')
        qty = int(request.POST.get('qty', '1'))
        
        # Находим вариант товара по размеру и цвету
        try:
            variant = ProductVariant.objects.get(
                product_id=product_id,
                size=size,
                color=color
            )
        except ProductVariant.DoesNotExist:
            messages.error(request, "Selected variant not available")
            return redirect(f'/product/{product_id}/')
        
        cart = _get_cart(request.user)
        
        # Считаем текущее общее количество товаров в корзине
        current_total = CartItem.objects.filter(cart=cart).aggregate(
            total_qty=Sum('quantity')
        )['total_qty'] or 0
        
        if current_total + qty > MAX_ITEMS_IN_CART:
            messages.error(request, f"Вы не можете добавить больше {MAX_ITEMS_IN_CART} товаров в корзину")
            return redirect(f'/product/{product_id}/')
        
        item, created = CartItem.objects.get_or_create(cart=cart, variant=variant)
        if not created:
            item.quantity += qty
        else:
            item.quantity = qty
        item.save()
        messages.success(request, "Added to cart")
    return redirect(f'/product/{product_id}/')

@login_required
def update_item(request, item_id):
    if request.method == 'POST':
        qty = int(request.POST.get('qty', '1'))
        item = get_object_or_404(CartItem, id=item_id, cart__user=request.user)
        item.quantity = qty
        item.save()
    return redirect('/cart/')

@login_required
def remove_item(request, item_id):
    if request.method == 'POST':
        item = get_object_or_404(CartItem, id=item_id, cart__user=request.user)
        item.delete()
    return redirect('/cart/')

@login_required
def apply_coupon(request):
    if request.method == 'POST':
        code = request.POST.get('code','').strip()
        cart = _get_cart(request.user)
        cart.coupon_code = code
        cart.save()
    return redirect('/cart/')
