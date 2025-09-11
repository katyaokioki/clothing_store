from rest_framework import serializers
from .models import Order, OrderItem, Coupon
from catalog.serializers import ProductVariantSerializer

class CouponSerializer(serializers.ModelSerializer):
    class Meta:
        model = Coupon
        fields = ['id','code','discount_percent','active']

class OrderItemSerializer(serializers.ModelSerializer):
    variant = ProductVariantSerializer(read_only=True)
    class Meta:
        model = OrderItem
        fields = ['id','variant','quantity','price']

class OrderSerializer(serializers.ModelSerializer):
    items = OrderItemSerializer(many=True, read_only=True)
    class Meta:
        model = Order
        fields = ['id','user','status','tracking_number','coupon','total_amount','created_at','items']
        read_only_fields = ['user','total_amount','created_at','tracking_number']
