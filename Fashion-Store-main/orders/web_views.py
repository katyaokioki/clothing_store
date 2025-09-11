from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from decimal import Decimal
from .models import Order, OrderItem, Coupon
from cart.models import Cart, CartItem
from accounts.models import UserAddress
from accounts.web_views import add_address

@login_required
def list_orders(request):
    qs = Order.objects.filter(user=request.user).order_by('-created_at')
    return render(request, 'orders/orders.html', {'orders': qs})

@login_required
def order_detail(request, pk):
    order = get_object_or_404(Order, pk=pk, user=request.user)
    return render(request, 'orders/order_detail.html', {'order': order})


@login_required
def checkout(request):
    cart, _ = Cart.objects.get_or_create(user=request.user)
    items = cart.items.select_related('variant')
    if not items.exists():
        add_address(request)
        messages.error(request, "Cart is empty")
        return redirect('/cart/')

    # --- Check if user has address ---
    addresses = request.user.addresses.all()
    if not addresses.exists():
        # If no address, ask user to add one
        # new template for address form
        add_address(request)
        # messages.success(request, f"Order #{order.id} placed successfully!")
        # return redirect(f'/orders/{order.id}/')
    # --- Normal checkout flow once address exists ---
    addresses = request.user.addresses.all()
    subtotal = sum([i.subtotal for i in items], Decimal('0.00'))
    coupon = None
    discount = Decimal('0.00')
    

    if cart.coupon_code:
        coupon = Coupon.objects.filter(code__iexact=cart.coupon_code, active=True).first()
        if coupon:
            discount = coupon.apply(subtotal)
            coupon.active = False
            coupon.save()

    total = max(Decimal('0.00'), subtotal - discount)

    # Use first address (or later you can add selection logic)
    if request.method == "POST":
        # --- User selected an address ---
        address_id = request.POST.get("address_id")
        selected_address = get_object_or_404(addresses, id=address_id)

    order = Order.objects.create(
        user=request.user,
        coupon=coupon,
        total_amount=total,
        status='placed',
        tracking_number=f"TRK{order_id_seed()}",
       address= f"{selected_address.address_line}, {selected_address.city}, {selected_address.state}, {selected_address.postal_code}, {selected_address.country}"
    )

    for it in items:
        OrderItem.objects.create(order=order, variant=it.variant, quantity=it.quantity, price=it.variant.price)
        it.variant.stock = max(0, it.variant.stock - it.quantity)
        it.variant.save()

    cart.items.all().delete()
    cart.coupon_code = ''
    cart.save()

    messages.success(request, f"Order #{order.id} placed successfully!")
    return redirect(f'/orders/{order.id}/')

def order_id_seed():
    from random import randint
    return randint(100000, 999999)
