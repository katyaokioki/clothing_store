from django.contrib import admin
from django.utils.translation import gettext_lazy as _
from django.utils.html import format_html
from django.db.models import Sum, Count
from .models import Order, OrderItem, Coupon

class OrderItemInline(admin.TabularInline):
    """Inline для товаров в заказе"""
    model = OrderItem
    extra = 0
    fields = ('variant', 'quantity', 'price', 'get_subtotal_display')
    readonly_fields = ('get_subtotal_display', 'created_at')
    
    def get_subtotal_display(self, obj):
        """Возвращает стоимость товара с учетом количества"""
        return obj.subtotal
    get_subtotal_display.short_description = _('Стоимость')

@admin.register(Coupon)
class CouponAdmin(admin.ModelAdmin):
    """Административная панель для купонов"""
    
    list_display = (
        'code', 'name', 'discount_percent', 'discount_amount', 
        'min_order_amount', 'used_count', 'max_uses', 'active',
        'valid_from', 'valid_until', 'created_at'
    )
    list_filter = (
        'active', 'discount_percent', 'created_at', 'valid_from', 'valid_until'
    )
    search_fields = ('code', 'name', 'description')
    ordering = ('-created_at',)
    list_display_links = ('code', 'name')
    
    # Поля только для чтения
    readonly_fields = ('used_count', 'created_at', 'updated_at')
    
    # Иерархия по датам
    date_hierarchy = 'created_at'
    
    # Поля для редактирования
    fieldsets = (
        (_('Основная информация'), {
            'fields': ('code', 'name', 'description')
        }),
        (_('Скидка'), {
            'fields': ('discount_percent', 'discount_amount', 'min_order_amount')
        }),
        (_('Ограничения'), {
            'fields': ('max_uses', 'used_count')
        }),
        (_('Время действия'), {
            'fields': ('valid_from', 'valid_until')
        }),
        (_('Статус'), {
            'fields': ('active',)
        }),
        (_('Даты'), {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    def get_queryset(self, request):
        """Оптимизирует запросы"""
        return super().get_queryset(request).select_related()

@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    """Административная панель для заказов"""
    
    list_display = (
        'order_number', 'user', 'get_status_display_ru', 'get_payment_status_display_ru',
        'get_total_amount_display', 'get_items_count', 'payment_method',
        'tracking_number', 'created_at'
    )
    list_filter = (
        'status', 'payment_status', 'payment_method', 'created_at', 'updated_at'
    )
    search_fields = (
        'order_number', 'user__email', 'user__name', 'tracking_number',
        'address', 'phone'
    )
    ordering = ('-created_at',)
    list_display_links = ('order_number', 'user')
    
    # Поля только для чтения
    readonly_fields = (
        'order_number', 'created_at', 'updated_at', 'get_items_count',
        'get_total_quantity', 'get_subtotal_display', 'get_discount_display',
        'get_total_amount_display'
    )
    
    # Поля для поиска по связанным моделям
    raw_id_fields = ('user', 'coupon')
    
    # Иерархия по датам
    date_hierarchy = 'created_at'
    
    # Inline для товаров в заказе
    inlines = [OrderItemInline]
    
    # Поля для редактирования
    fieldsets = (
        (_('Основная информация'), {
            'fields': ('user', 'order_number', 'status', 'payment_status', 'payment_method')
        }),
        (_('Доставка'), {
            'fields': ('tracking_number', 'address', 'phone', 'estimated_delivery', 'delivered_at')
        }),
        (_('Финансы'), {
            'fields': ('coupon', 'get_subtotal_display', 'get_discount_display', 'shipping_cost', 'get_total_amount_display')
        }),
        (_('Дополнительно'), {
            'fields': ('notes',)
        }),
        (_('Статистика'), {
            'fields': ('get_items_count', 'get_total_quantity'),
            'classes': ('collapse',)
        }),
        (_('Даты'), {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    actions = ['mark_as_processing', 'mark_as_shipped', 'mark_as_delivered', 'mark_as_cancelled']
    
    @admin.display(description=_('Статус'))
    def get_status_display_ru(self, obj):
        """Возвращает статус на русском языке"""
        status = obj.get_status_display_ru()
        if obj.status == 'cancelled':
            return format_html('<span style="color: red;">{}</span>', status)
        elif obj.status == 'delivered':
            return format_html('<span style="color: green;">{}</span>', status)
        elif obj.status in ['shipped', 'out_for_delivery']:
            return format_html('<span style="color: blue;">{}</span>', status)
        return status
    
    @admin.display(description=_('Статус оплаты'))
    def get_payment_status_display_ru(self, obj):
        """Возвращает статус оплаты на русском языке"""
        status = obj.get_payment_status_display_ru()
        if obj.payment_status == 'paid':
            return format_html('<span style="color: green;">{}</span>', status)
        elif obj.payment_status == 'failed':
            return format_html('<span style="color: red;">{}</span>', status)
        return status
    
    @admin.display(description=_('Итоговая сумма'))
    def get_total_amount_display(self, obj):
        """Возвращает итоговую сумму заказа"""
        return format_html(
            '<strong style="color: blue;">{}</strong>',
            obj.total_amount
        )
    
    @admin.display(description=_('Количество товаров'))
    def get_items_count(self, obj):
        """Возвращает количество товаров в заказе"""
        count = obj.get_items_count()
        if count > 0:
            return format_html(
                '<a href="{}?order__id__exact={}">{}</a>',
                '/admin/orders/orderitem/',
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
        return obj.subtotal
    
    @admin.display(description=_('Сумма скидки'))
    def get_discount_display(self, obj):
        """Возвращает сумму скидки"""
        discount = obj.discount_amount
        if discount > 0:
            return format_html(
                '<span style="color: green;">-{}</span>',
                discount
            )
        return discount
    
    @admin.action(description=_('Отметить как "В обработке"'))
    def mark_as_processing(self, request, queryset):
        """Отмечает заказы как находящиеся в обработке"""
        updated = queryset.update(status='processing')
        self.message_user(request, f'{updated} заказов отмечено как "В обработке"')
    
    @admin.action(description=_('Отметить как "Отправлен"'))
    def mark_as_shipped(self, request, queryset):
        """Отмечает заказы как отправленные"""
        updated = queryset.update(status='shipped')
        self.message_user(request, f'{updated} заказов отмечено как "Отправлен"')
    
    @admin.action(description=_('Отметить как "Доставлен"'))
    def mark_as_delivered(self, request, queryset):
        """Отмечает заказы как доставленные"""
        updated = queryset.update(status='delivered')
        self.message_user(request, f'{updated} заказов отмечено как "Доставлен"')
    
    @admin.action(description=_('Отметить как "Отменен"'))
    def mark_as_cancelled(self, request, queryset):
        """Отмечает заказы как отмененные"""
        updated = queryset.update(status='cancelled')
        self.message_user(request, f'{updated} заказов отмечено как "Отменен"')

@admin.register(OrderItem)
class OrderItemAdmin(admin.ModelAdmin):
    """Административная панель для товаров в заказах"""
    
    list_display = (
        'order', 'get_product_name', 'get_variant_display', 'quantity',
        'price', 'get_subtotal_display', 'created_at'
    )
    list_filter = (
        'created_at', 'variant__size', 'variant__color'
    )
    search_fields = (
        'order__order_number', 'order__user__email', 'order__user__name',
        'variant__product__name', 'variant__size', 'variant__color'
    )
    ordering = ('-created_at',)
    list_display_links = ('order',)
    
    # Поля только для чтения
    readonly_fields = ('created_at', 'get_subtotal_display')
    
    # Поля для поиска по связанным моделям
    raw_id_fields = ('order', 'variant')
    
    # Иерархия по датам
    date_hierarchy = 'created_at'
    
    # Поля для редактирования
    fieldsets = (
        (_('Основная информация'), {
            'fields': ('order', 'variant', 'quantity', 'price')
        }),
        (_('Стоимость'), {
            'fields': ('get_subtotal_display',)
        }),
        (_('Даты'), {
            'fields': ('created_at',),
            'classes': ('collapse',)
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
    
    @admin.display(description=_('Стоимость'))
    def get_subtotal_display(self, obj):
        """Возвращает стоимость товара с учетом количества"""
        return obj.subtotal
