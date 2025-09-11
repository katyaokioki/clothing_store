from rest_framework import serializers
from .models import Category, Product, ProductVariant, Review

class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ['id','name','slug']

class ProductVariantSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductVariant
        fields = ['id','size','color','price','stock']

class ProductSerializer(serializers.ModelSerializer):
    category = CategorySerializer(read_only=True)
    category_id = serializers.PrimaryKeyRelatedField(source='category', queryset=Category.objects.all(), write_only=True)
    variants = ProductVariantSerializer(many=True, read_only=True)
    class Meta:
        model = Product
        fields = ['id','name','description','base_price','image','category','category_id','variants','created_at']

class ReviewSerializer(serializers.ModelSerializer):
    user_email = serializers.ReadOnlyField(source='user.email')
    class Meta:
        model = Review
        fields = ['id','product','user','user_email','rating','comment','created_at']
        read_only_fields = ['user','user_email','created_at']
