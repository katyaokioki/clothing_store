from rest_framework import viewsets, permissions, status
from rest_framework.response import Response
from .models import Cart, CartItem
from catalog.models import ProductVariant
from .serializers import CartSerializer, CartItemSerializer

class CartViewSet(viewsets.ModelViewSet):
    serializer_class = CartSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Cart.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

class CartItemViewSet(viewsets.ModelViewSet):
    serializer_class = CartItemSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return CartItem.objects.filter(cart__user=self.request.user)

    def create(self, request, *args, **kwargs):
        variant_id = request.data.get('variant_id')
        qty = int(request.data.get('quantity', 1))
        variant = ProductVariant.objects.get(id=variant_id)
        cart, _ = Cart.objects.get_or_create(user=request.user)
        item, created = CartItem.objects.get_or_create(cart=cart, variant=variant)
        item.quantity = item.quantity + qty if not created else qty
        item.save()
        return Response(CartItemSerializer(item).data, status=status.HTTP_201_CREATED)
