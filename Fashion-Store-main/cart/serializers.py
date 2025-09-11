from rest_framework import serializers
from .models import Cart, CartItem
from catalog.serializers import ProductVariantSerializer

class CartItemSerializer(serializers.ModelSerializer):
    variant = ProductVariantSerializer(read_only=True)
    variant_id = serializers.IntegerField(write_only=True)
    class Meta:
        model = CartItem
        fields = ['id','variant','variant_id','quantity','cart']

class CartSerializer(serializers.ModelSerializer):
    items = CartItemSerializer(many=True, read_only=True)
    class Meta:
        model = Cart
        fields = ['id','user','coupon_code','items']
        read_only_fields = ['user']
