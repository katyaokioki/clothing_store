from rest_framework import viewsets, permissions, filters
from django_filters.rest_framework import DjangoFilterBackend
from .models import Category, Product, ProductVariant, Review
from .serializers import CategorySerializer, ProductSerializer, ProductVariantSerializer, ReviewSerializer

class IsAdminOrReadOnly(permissions.BasePermission):
    def has_permission(self, request, view):
        if request.method in permissions.SAFE_METHODS:
            return True
        return request.user and request.user.is_staff

class CategoryViewSet(viewsets.ModelViewSet):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    permission_classes = [IsAdminOrReadOnly]
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['name']

class ProductViewSet(viewsets.ModelViewSet):
    queryset = Product.objects.all().select_related('category').prefetch_related('variants')
    serializer_class = ProductSerializer
    permission_classes = [IsAdminOrReadOnly]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = {'category':['exact'],'variants__size':['exact'],'variants__color':['exact'],'base_price':['gte','lte']}
    search_fields = ['name','description']
    ordering_fields = ['base_price','created_at']

class ProductVariantViewSet(viewsets.ModelViewSet):
    queryset = ProductVariant.objects.all()
    serializer_class = ProductVariantSerializer
    permission_classes = [IsAdminOrReadOnly]
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['size','color','product']

class ReviewViewSet(viewsets.ModelViewSet):
    queryset = Review.objects.select_related('product','user').all()
    serializer_class = ReviewSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)
