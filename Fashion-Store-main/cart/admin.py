from django.contrib import admin
from django.utils.translation import gettext_lazy as _
from django.utils.html import format_html
from django.db.models import Sum, Count
from .models import Cart, CartItem

class CartItemInline(admin.TabularInline):
    """Inline для товаров в корзине"""
    model = CartItem
    extra = 0
    fields = ('variant', 'quantity', 'get_unit_price', 'get_subtotal_display')
    readonly_fields = ('get_unit_price', 'get_subtotal_display')
    
    def get_unit_price(self, obj):
        """Возвращает цену за единицу"""
        return obj.get_unit_price()
    get_unit_price.short_description = _('Цена за единицу')
    
    def get_subtotal_display(self, obj):
        """Возвращает стоимость товара с учетом количества"""
        return obj.subtotal
    get_subtotal_display.short_description = _('Стоимость')

@admin.register(Cart)
class CartAdmin(admin.ModelAdmin):
    """Административная панель для корзин"""
    
    list_display = (
        'user', 'get_items_count', 'get_total_quantity', 'get_subtotal_display',
        'get_discount_display', 'get_total_display', 'coupon_code'
    )
    list_filter = (
        'coupon_code', 'user__is_active', 'user__date_joined'
    )
    search_fields = (
        'user__email', 'user__name', 'coupon_code'
    )
    ordering = ('user',)
    list_display_links = ('user',)
    
    # Поля только для чтения
    readonly_fields = (
        'get_items_count', 'get_total_quantity',
        'get_subtotal_display', 'get_discount_display', 'get_total_display'
    )
    
    # Поля для поиска по связанным моделям
    raw_id_fields = ('user',)
    
    # Inline для товаров в корзине
    inlines = [CartItemInline]
    
    # Поля для редактирования
    fieldsets = (
        (_('Пользователь'), {
            'fields': ('user', 'coupon_code')
        }),
        (_('Статистика'), {
            'fields': (
                'get_items_count', 'get_total_quantity', 'get_subtotal_display',
                'get_discount_display', 'get_total_display'
            ),
            'classes': ('collapse',)
        }),
    )
    
    @admin.display(description=_('Количество товаров'))
    def get_items_count(self, obj):
        """Возвращает количество товаров в корзине"""
        count = obj.get_items_count()
        if count > 0:
            return format_html(
                '<a href="{}?cart__id__exact={}">{}</a>',
                '/admin/cart/cartitem/',
                obj.id,
                count
            )
        return count
    
    @admin.display(description=_('Общее количество'))
    def get_total_quantity(self, obj):
        """Возвращает общее количество товаров"""
        return obj.get_total_quantity()
    
    @admin.display(description=_('Сумма без скидки'))
    def get_subtotal_display(self, obj):
        """Возвращает сумму без скидки"""
        return obj.get_subtotal()
    
    @admin.display(description=_('Сумма скидки'))
    def get_discount_display(self, obj):
        """Возвращает сумму скидки"""
        discount = obj.get_discount_amount()
        if discount > 0:
            return format_html(
                '<span style="color: green;">-{}</span>',
                discount
            )
        return discount
    
    @admin.display(description=_('Итоговая сумма'))
    def get_total_display(self, obj):
        """Возвращает итоговую сумму"""
        total = obj.get_total()
        if total > 0:
            return format_html(
                '<strong style="color: blue;">{}</strong>',
                total
            )
        return total

@admin.register(CartItem)
class CartItemAdmin(admin.ModelAdmin):
    """Административная панель для товаров в корзине"""
    
    list_display = (
        'cart', 'get_product_name', 'get_variant_display', 'quantity',
        'get_unit_price_display', 'get_subtotal_display'
    )
    list_filter = (
        'variant__size', 'variant__color', 'variant__product__category',
        'variant__product__is_active', 'cart__user__is_active'
    )
    search_fields = (
        'cart__user__email', 'cart__user__name', 'variant__product__name',
        'variant__product__category__name', 'variant__size', 'variant__color'
    )
    ordering = ('cart',)
    list_display_links = ('cart',)
    
    # Поля только для чтения
    readonly_fields = ('get_subtotal_display',)
    
    # Поля для поиска по связанным моделям
    raw_id_fields = ('cart', 'variant')
    
    # Поля для редактирования
    fieldsets = (
        (_('Основная информация'), {
            'fields': ('cart', 'variant', 'quantity')
        }),
        (_('Цены'), {
            'fields': ('get_subtotal_display',)
        }),
    )
    
    @admin.display(description=_('Название товара'))
    def get_product_name(self, obj):
        """Возвращает название товара"""
        return obj.get_product_name()
    
    @admin.display(description=_('Вариант'))
    def get_variant_display(self, obj):
        """Возвращает отображение варианта"""
        return obj.get_variant_display()
    
    @admin.display(description=_('Цена за единицу'))
    def get_unit_price_display(self, obj):
        """Возвращает цену за единицу"""
        return obj.get_unit_price()
    
    @admin.display(description=_('Стоимость'))
    def get_subtotal_display(self, obj):
        """Возвращает стоимость товара с учетом количества"""
        return obj.subtotal
