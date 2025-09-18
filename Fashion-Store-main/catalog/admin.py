from django.contrib import admin
from django.utils.translation import gettext_lazy as _
from django.utils.html import format_html
from django.urls import reverse
from django.db.models import Count, Sum
from .models import Category, Product, ProductVariant, Review, OtherCategory, ReviewImage, Collection, ProductCollection
import io
from reportlab.pdfgen import canvas
from django.http import FileResponse

class ProductVariantInline(admin.TabularInline):
    """Inline для вариантов товара"""
    model = ProductVariant
    extra = 1
    fields = ('size', 'color', 'price', 'stock', 'sku', 'is_active')
    readonly_fields = ('created_at', 'updated_at')

class ReviewImageInline(admin.TabularInline):
    """Inline для изображений отзывов"""
    model = ReviewImage
    extra = 1
    fields = ('image', 'alt_text')


class ProductCollectionInline(admin.TabularInline):
    model = ProductCollection
    extra = 0
    raw_id_fields = ('collection',)
    fields = ('collection', 'order', 'featured_until', 'added_at')
    readonly_fields = ('added_at',)


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    """Административная панель для категорий"""
    
    list_display = (
        'name', 'slug', 'get_products_count', 'is_active', 
        'sort_order', 'created_at'
    )
    list_filter = ('is_active', 'created_at')
    search_fields = ('name', 'slug', 'description')
    ordering = ('sort_order', 'name')
    list_display_links = ('name',)
    prepopulated_fields = {'slug': ('name',)}
    
    # Поля только для чтения
    readonly_fields = ('created_at', 'updated_at')
    
    # Иерархия по датам
    date_hierarchy = 'created_at'
    
    # Поля для редактирования
    fieldsets = (
        (None, {
            'fields': ('name', 'slug', 'description', 'image')
        }),
        (_('Настройки'), {
            'fields': ('is_active', 'sort_order')
        }),
        (_('Даты'), {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    @admin.display(description=_('Количество товаров'))
    def get_products_count(self, obj):
        """Возвращает количество товаров в категории"""
        count = obj.get_products_count()
        if count > 0:
            return format_html(
                '<a href="{}?category__id__exact={}">{}</a>',
                '/admin/catalog/product/',
                obj.id,
                count
            )
        return count

@admin.register(OtherCategory)
class OtherCategoryAdmin(admin.ModelAdmin):
    """Административная панель для дополнительных категорий"""
    
    list_display = ('name', 'slug', 'is_active', 'created_at')
    list_filter = ('is_active', 'created_at')
    search_fields = ('name', 'slug', 'description')
    ordering = ('name',)
    list_display_links = ('name',)
    prepopulated_fields = {'slug': ('name',)}
    
    # Поля только для чтения
    readonly_fields = ('created_at',)
    
    # Поля для редактирования
    fieldsets = (
        (None, {
            'fields': ('name', 'slug', 'description')
        }),
        (_('Настройки'), {
            'fields': ('is_active',)
        }),
        (_('Даты'), {
            'fields': ('created_at',),
            'classes': ('collapse',)
        }),
    )

@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    """Административная панель для товаров"""
    
    list_display = (
        'name', 'category', 'get_current_price_display', 'get_discount_display',
        'get_variants_count', 'get_total_stock', 'get_rating_display',
        'is_active', 'is_featured', 'is_new', 'created_at'
    )
    list_filter = (
        'is_active', 'is_featured', 'is_new', 'category', 'other_category',
        'created_at', 'updated_at', 'category__is_active'
    )
    search_fields = (
        'name', 'description', 'short_description', 'category__name',
        'other_category__name', 'variants__size', 'variants__color'
    )
    ordering = ('-created_at',)
    list_display_links = ('name',)
    
    # Поля только для чтения
    readonly_fields = (
        'created_at', 'updated_at', 'get_variants_count', 
        'get_total_stock', 'get_average_rating', 'get_reviews_count'
    )
    
    # Поля для поиска по связанным моделям
    raw_id_fields = ('category', 'other_category')
    
    # Иерархия по датам
    date_hierarchy = 'created_at'
    
    # Inline для вариантов товара
    inlines = [ProductVariantInline, ProductCollectionInline]
    
    # Поля для редактирования
    fieldsets = (
        (_('Основная информация'), {
            'fields': ('name', 'description', 'short_description', 'image')
        }),
        (_('Цены'), {
            'fields': ('base_price', 'sale_price')
        }),
        (_('Категории'), {
            'fields': ('category', 'other_category')
        }),
        (_('Характеристики'), {
            'fields': ('weight', 'dimensions')
        }),
        (_('Настройки'), {
            'fields': ('is_active', 'is_featured', 'is_new')
        }),
        (_('Статистика'), {
            'fields': (
                'get_variants_count', 'get_total_stock', 
                'get_average_rating', 'get_reviews_count'
            ),
            'classes': ('collapse',)
        }),
        (_('Даты'), {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    @admin.display(description=_('Текущая цена'))
    def get_current_price_display(self, obj):
        """Возвращает текущую цену товара"""
        current_price = obj.get_current_price()
        if obj.sale_price and obj.sale_price < obj.base_price:
            return format_html(
                '<span style="color: red; text-decoration: line-through;">{}</span> <strong>{}</strong>',
                obj.base_price,
                current_price
            )
        return current_price
    
    @admin.display(description=_('Скидка'))
    def get_discount_display(self, obj):
        """Возвращает информацию о скидке"""
        discount = obj.get_discount_percent()
        if discount > 0:
            return format_html(
                '<span style="color: green;">-{}%</span>',
                discount
            )
        return '-'
    
    @admin.display(description=_('Варианты'))
    def get_variants_count(self, obj):
        """Возвращает количество вариантов товара"""
        count = obj.get_variants_count()
        if count > 0:
            return format_html(
                '<a href="{}?product__id__exact={}">{}</a>',
                '/admin/catalog/productvariant/',
                obj.id,
                count
            )
        return count
    
    @admin.display(description=_('Остаток'))
    def get_total_stock(self, obj):
        """Возвращает общий остаток на складе"""
        stock = obj.get_total_stock()
        if stock == 0:
            return format_html('<span style="color: red;">{}</span>', stock)
        elif stock <= 10:
            return format_html('<span style="color: orange;">{}</span>', stock)
        return stock
    
    @admin.display(description=_('Рейтинг'))
    def get_rating_display(self, obj):
        """Возвращает рейтинг товара"""
        rating = obj.get_average_rating()
        reviews_count = str(obj.get_reviews_count())
        if rating > 0:
            rating = f"{int(rating)}"
            full_stars = max(0, min(5, int(rating)))  # целая часть, обрезаем до 0..5
            stars = "★" * full_stars + "☆" * (5 - int(rating))
            return format_html(
                '{} ({})<br><small>{} отзывов</small>',
                stars, rating, reviews_count
            )
        return 'Нет отзывов'
    @admin.action(description='Скачать PDF по выбранным товарам')
    def export_products_pdf(self, request, queryset):
        buf = io.BytesIO()
        p = canvas.Canvas(buf)
        y = 800
        for obj in queryset:
            line = f'{obj.name} — цена: {obj.get_current_price()}'
            p.drawString(40, y, line)
            y -= 20
            if y < 60:
                p.showPage()
                y = 800
        p.showPage()
        p.save()
        buf.seek(0)
        return FileResponse(buf, as_attachment=True, filename='products.pdf')
    actions = ['export_products_pdf']

@admin.register(ProductVariant)
class ProductVariantAdmin(admin.ModelAdmin):
    """Административная панель для вариантов товаров"""
    
    list_display = (
        'product', 'size', 'color', 'price', 'stock', 'sku',
        'get_stock_status_display', 'is_active', 'created_at'
    )
    list_filter = (
        'is_active', 'size', 'color', 'product__category', 'product__is_active',
        'created_at', 'stock'
    )
    search_fields = (
        'product__name', 'product__category__name', 'size', 'color', 'sku'
    )
    ordering = ('product', 'size', 'color')
    list_display_links = ('product',)
    
    # Поля только для чтения
    readonly_fields = ('created_at', 'updated_at')
    
    # Поля для поиска по связанным моделям
    raw_id_fields = ('product',)
    
    # Иерархия по датам
    date_hierarchy = 'created_at'
    
    # Поля для редактирования
    fieldsets = (
        (_('Основная информация'), {
            'fields': ('product', 'size', 'color', 'sku')
        }),
        (_('Цена и остаток'), {
            'fields': ('price', 'stock')
        }),
        (_('Изображение'), {
            'fields': ('image',)
        }),
        (_('Настройки'), {
            'fields': ('is_active',)
        }),
        (_('Даты'), {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    @admin.display(description=_('Статус наличия'))
    def get_stock_status_display(self, obj):
        """Возвращает статус наличия товара"""
        status = obj.get_stock_status()
        if status == "Нет в наличии":
            return format_html('<span style="color: red;">{}</span>', status)
        elif status == "Заканчивается":
            return format_html('<span style="color: orange;">{}</span>', status)
        return format_html('<span style="color: green;">{}</span>', status)

@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    """Административная панель для отзывов"""
    
    list_display = (
        'product', 'user', 'rating', 'get_rating_display', 'is_approved',
        'is_verified_purchase', 'created_at'
    )
    list_filter = (
        'rating', 'is_approved', 'is_verified_purchase', 'created_at',
        'product__category', 'product__is_active', 'user__is_active'
    )
    search_fields = (
        'product__name', 'product__category__name', 'user__email', 'user__name', 'comment'
    )
    ordering = ('-created_at',)
    list_display_links = ('product', 'user')
    
    # Поля только для чтения
    readonly_fields = ('created_at', 'updated_at')
    
    # Поля для поиска по связанным моделям
    raw_id_fields = ('product', 'user')
    
    # Иерархия по датам
    date_hierarchy = 'created_at'
    
    # Inline для изображений отзывов
    inlines = [ReviewImageInline]
    
    # Поля для редактирования
    fieldsets = (
        (_('Основная информация'), {
            'fields': ('product', 'user', 'rating', 'comment')
        }),
        (_('Статус'), {
            'fields': ('is_approved', 'is_verified_purchase')
        }),
        (_('Даты'), {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    @admin.display(description=_('Оценка'))
    def get_rating_display(self, obj):
        """Возвращает отображаемую оценку"""
        return obj.get_rating_display()

@admin.register(ReviewImage)
class ReviewImageAdmin(admin.ModelAdmin):
    """Административная панель для изображений отзывов"""
    
    list_display = ('review', 'get_image_preview', 'alt_text', 'created_at')
    list_filter = ('created_at', 'review__rating', 'review__is_approved')
    search_fields = (
        'review__product__name', 'review__product__category__name', 
        'review__user__email', 'review__user__name', 'alt_text'
    )
    ordering = ('-created_at',)
    list_display_links = ('review',)
    
    # Поля только для чтения
    readonly_fields = ('created_at',)
    
    # Поля для поиска по связанным моделям
    raw_id_fields = ('review',)
    
    # Иерархия по датам
    date_hierarchy = 'created_at'
    
    # Поля для редактирования
    fieldsets = (
        (_('Основная информация'), {
            'fields': ('review', 'image', 'alt_text')
        }),
        (_('Даты'), {
            'fields': ('created_at',),
            'classes': ('collapse',)
        }),
    )
    
    @admin.display(description=_('Предпросмотр'))
    def get_image_preview(self, obj):
        """Возвращает предпросмотр изображения"""
        if obj.image:
            return format_html(
                '<img src="{}" style="max-height: 50px; max-width: 50px;" />',
                obj.image.url
            )
        return 'Нет изображения'


