from django.shortcuts import render, get_object_or_404
from django.db.models import Q
from .models import Product, Category, ProductVariant, Review, OtherCategory, ReviewImage
from django.db.models import Sum, F, Value
from django.db.models.functions import Coalesce
from django.db.models import OuterRef, Subquery
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_POST
from django.shortcuts import get_object_or_404, redirect
from orders.models import OrderItem


from django.views.decorators.cache import cache_page
from django.http import JsonResponse
from django.core.paginator import Paginator
from django.db.models import Q
from catalog.models import Product


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



@login_required
@require_POST
def create_review(request, pk):
    product = get_object_or_404(Product, pk=pk)
    # Валидация рейтинга
    rating_raw = request.POST.get('rating')
    try:
        rating = int(rating_raw)
    except (TypeError, ValueError):
        return redirect('product_detail', pk=product.pk)

    if rating < 1 or rating > 5:
        return redirect('product_detail', pk=product.pk)

    comment = (request.POST.get('comment') or '').strip()

    # Создаём отзыв (по умолчанию на модерации)
    review = Review.objects.create(
        product=product,
        user=request.user,
        rating=rating,
        comment=comment,
        is_approved=False,
        is_verified_purchase=False,
    )

    # Помечаем «подтвержденную покупку», если есть OrderItem этого пользователя по данному товару
    if OrderItem.objects.filter(
        order__user=request.user,
        variant__product=product
    ).exists():
        review.is_verified_purchase = True
        review.save(update_fields=['is_verified_purchase'])

    # Сохраняем прикреплённые изображения (если есть)
    for f in request.FILES.getlist('images'):
        ReviewImage.objects.create(review=review, image=f)

    return redirect('product_detail', pk=product.pk)


@cache_page(60)  # кэш на 60 секунд
def catalog_list(request):
    # Параметры фильтрации/сортировки/пагинации
    q = request.GET.get("q")  # поиск по имени/описанию
    category = request.GET.get("category")  # slug категории
    other_category = request.GET.get("other_category")  # slug доп.категории
    only_active = request.GET.get("active", "1")  # фильтр активных
    is_featured = request.GET.get("featured")  # рекомендуемые
    ordering = request.GET.get("ordering", "-created_at")  # например "-created_at" или "name"

    page = int(request.GET.get("page", 1))
    per_page = int(request.GET.get("per_page", 12))

    qs = Product.objects.select_related("category", "other_category").all()

    # Фильтры
    if only_active == "1":
        qs = qs.filter(is_active=True)
    if q:
        qs = qs.filter(Q(name__icontains=q) | Q(description__icontains=q) | Q(short_description__icontains=q))
    if category:
        qs = qs.filter(category__slug=category, category__is_active=True)
    if other_category:
        qs = qs.filter(other_category__slug=other_category, other_category__is_active=True)
    if is_featured in ("0", "1"):
        qs = qs.filter(is_featured=(is_featured == "1"))

    # Сортировка (белый список полей, чтобы не дать инъекцию)
    allowed_order = {"name", "-name", "created_at", "-created_at", "base_price", "-base_price", "sale_price", "-sale_price"}
    if ordering not in allowed_order:
        ordering = "-created_at"
    qs = qs.order_by(ordering)

    # Пагинация
    paginator = Paginator(qs, per_page)
    page_obj = paginator.get_page(page)

    # Сериализация
    def price(p):
        return float(p.sale_price if p.sale_price else p.base_price)

    items = [
        {
            "id": p.id,
            "name": p.name,
            "category": p.category.name if p.category else None,
            "category_slug": p.category.slug if p.category else None,
            "other_category": p.other_category.name if p.other_category else None,
            "is_featured": p.is_featured,
            "is_new": p.is_new,
            "price": price(p),
            "discount_percent": p.get_discount_percent(),
        }
        for p in page_obj.object_list
    ]

    data = {
        "count": paginator.count,
        "num_pages": paginator.num_pages,
        "page": page_obj.number,
        "results": items,
    }
    return JsonResponse(data, json_dumps_params={"ensure_ascii": False})
