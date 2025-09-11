from django.shortcuts import render, get_object_or_404
from django.db.models import Q
from .models import Product, Category, ProductVariant, Review,OtherCategory
from django.db.models import Sum, F, Value
from django.db.models.functions import Coalesce
from django.db.models import OuterRef, Subquery

def home(request):
    qs = Product.objects.all().select_related('category','other_category')
    category_slug = request.GET.get('category')
    other_category_slug = request.GET.get('other_category')
    q = request.GET.get('q')
    min_price = request.GET.get('min_price')
    max_price = request.GET.get('max_price')
    # if category_slug and other_category_slug:
    #     qs = qs.filter(Q(category__slug=category_slug) & Q(other_category__slug=other_category_slug))
    if category_slug:
        qs = qs.filter(category__slug=category_slug)
    if other_category_slug:
        qs = qs.filter(other_category__slug=other_category_slug)
    if q:
        qs = qs.filter(Q(name__icontains=q) | Q(description__icontains=q))
    if min_price:
        qs = qs.filter(base_price__gte=min_price)
    if max_price:
        qs = qs.filter(base_price__lte=max_price)
    categories = Category.objects.all()
    return render(request, 'catalog/home.html', {'products': qs, 'categories': categories,})

def product_list(request):
    qs =  (Product.objects
    .select_related("category")  # only FK
    .annotate(
        total_quantity=Coalesce(Sum("variants__order_items__quantity"), Value(0))
    )
    .order_by("-total_quantity"))
    category_slug = request.GET.getlist('category')
    print(f"testing the sug {category_slug}")
    sort = request.GET.get('sort')
    other_category_slug = request.GET.getlist('other_category')
    print(f"testing the othersug {other_category_slug}")
    q = request.GET.get('q')
    min_price = request.GET.get('min_price')
    max_price = request.GET.get('max_price')
    if sort == "low-high":
        qs = qs.order_by('base_price')
    if sort == "high-low":
        qs = qs.order_by('-base_price')
    if sort == "newest":
        qs = qs.order_by('-created_at')
    if sort == "recommended":
        qs = qs.annotate(
        total_quantity=Coalesce(Sum("variants__order_items__quantity"), Value(0))
    ).order_by("-total_quantity")

    if category_slug:
        qs = qs.filter(category__slug__in=category_slug)
    if other_category_slug:
        qs = qs.filter(other_category__slug__in=other_category_slug)
    if q:
        qs = qs.filter(Q(name__icontains=q) | Q(description__icontains=q))
    if min_price:
        qs = qs.filter(base_price__gte=min_price)
    if max_price:
        qs = qs.filter(base_price__lte=max_price)
    categories = Category.objects.all()
    other_categories = OtherCategory.objects.all()
    heading = "Outfit For Men & Women"
    other_heading=""
    if category_slug:
        cat = Category.objects.filter(slug__in=category_slug).first()
        if cat:
            heading = f"Outfit For {cat.name}"
    if other_category_slug:
        cats = OtherCategory.objects.filter(slug__in=other_category_slug).values_list("name", flat=True)
        other_heading = ", ".join(cats)
        heading = f"{heading} - {other_heading}"
    return render(request, 'catalog/product_list.html', {'products': qs, 'categories': categories,'other_categories':other_categories,'heading':heading})

def product_detail(request, pk):
    product = get_object_or_404(Product, pk=pk)
    variants = product.variants.all()
    # Subquery to get first variant per unique size
    size_subquery = product.variants.filter(size=OuterRef("size")).order_by("id")

    unique_size_variants = (
        product.variants.filter(id=Subquery(size_subquery.values("id")[:1]))
    )

    # Same for color
    color_subquery = product.variants.filter(color=OuterRef("color")).order_by("id")

    unique_color_variants = (
        product.variants.filter(id=Subquery(color_subquery.values("id")[:1]))
    )
    # simple outfit suggestion: same category, different product
    suggestions = Product.objects.filter(category=product.category).exclude(id=product.id)[:5]
    reviews = product.reviews.select_related('user').prefetch_related('reviews_image').all()
    return render(request, 'catalog/product_detail.html', {
        'product': product, 'variants': variants, 'suggestions': suggestions, 'reviews': reviews,'unique_sizes':unique_size_variants,'unique_colors':unique_color_variants
    })
