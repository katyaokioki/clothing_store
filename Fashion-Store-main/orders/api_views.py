from rest_framework import viewsets, permissions
from rest_framework.decorators import action
from rest_framework.response import Response
from decimal import Decimal
from .models import Order, OrderItem, Coupon
from cart.models import Cart
from .serializers import OrderSerializer, CouponSerializer

class IsAdminOrOwner(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        return request.user.is_staff or obj.user == request.user
    def has_permission(self, request, view):
        return request.user and request.user.is_authenticated

class OrderViewSet(viewsets.ModelViewSet):
    serializer_class = OrderSerializer
    permission_classes = [IsAdminOrOwner]

    def get_queryset(self):
        if self.request.user.is_staff:
            return Order.objects.all().order_by('-created_at')
        return Order.objects.filter(user=self.request.user).order_by('-created_at')

    @action(detail=False, methods=['post'])
    def create_from_cart(self, request):
        cart, _ = Cart.objects.get_or_create(user=request.user)
        items = cart.items.select_related('variant').all()
        if not items:
            return Response({'detail':'Cart empty'}, status=400)
        subtotal = sum([i.subtotal for i in items], Decimal('0.00'))
        coupon = None
        discount = Decimal('0.00')
        if cart.coupon_code:
            coupon = Coupon.objects.filter(code__iexact=cart.coupon_code, active=True).first()
            if coupon:
                discount = coupon.apply(subtotal)
        total = max(Decimal('0.00'), subtotal - discount)
        order = Order.objects.create(user=request.user, coupon=coupon, total_amount=total, status='paid', tracking_number=f"TRK{self.request.user.id}{order.id if hasattr(order,'id') else ''}")
        for it in items:
            OrderItem.objects.create(order=order, variant=it.variant, quantity=it.quantity, price=it.variant.price)
            it.variant.stock = max(0, it.variant.stock - it.quantity)
            it.variant.save()
        cart.items.all().delete()
        cart.coupon_code = ''
        cart.save()
        return Response(OrderSerializer(order).data, status=201)

class CouponViewSet(viewsets.ModelViewSet):
    queryset = Coupon.objects.all()
    serializer_class = CouponSerializer
    permission_classes = [permissions.IsAdminUser]
