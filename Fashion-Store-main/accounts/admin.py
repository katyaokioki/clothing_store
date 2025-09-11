from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.utils.translation import gettext_lazy as _
from django.utils.html import format_html
from .models import User, UserAddress

@admin.register(User)
class UserAdmin(BaseUserAdmin):
    """Административная панель для пользователей"""
    
    list_display = (
        'email', 'name', 'phone', 'is_active', 'is_staff', 
        'get_orders_count', 'get_cart_items_count', 
        'date_joined'
    )
    list_filter = (
        'is_active', 'is_staff', 'is_superuser', 'date_joined'
    )
    search_fields = ('email', 'name', 'phone')
    ordering = ('-date_joined',)
    list_display_links = ('email', 'name')
    
    # Поля только для чтения
    readonly_fields = ('last_login', 'date_joined')
    
    # Поля для поиска по связанным моделям
    raw_id_fields = ('groups', 'user_permissions')
    
    # Горизонтальные фильтры для групп и разрешений
    filter_horizontal = ('groups', 'user_permissions')
    
    # Иерархия по датам
    date_hierarchy = 'date_joined'
    
    # Поля для редактирования
    fieldsets = (
        (None, {
            'fields': ('email', 'password')
        }),
        (_('Личная информация'), {
            'fields': ('name', 'phone')
        }),
        (_('Разрешения'), {
            'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions')
        }),
        (_('Важные даты'), {
            'fields': ('last_login', 'date_joined')
        }),
    )
    
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('email', 'name', 'password1', 'password2'),
        }),
    )
    
    @admin.display(description=_('Количество заказов'))
    def get_orders_count(self, obj):
        """Возвращает количество заказов пользователя"""
        count = obj.orders.count()
        if count > 0:
            return format_html(
                '<a href="{}?user__id__exact={}">{}</a>',
                '/admin/orders/order/',
                obj.id,
                count
            )
        return count
    
    @admin.display(description=_('Товары в корзине'))
    def get_cart_items_count(self, obj):
        """Возвращает количество товаров в корзине пользователя"""
        try:
            return obj.cart.get_items_count()
        except:
            return 0

@admin.register(UserAddress)
class UserAddressAdmin(admin.ModelAdmin):
    """Административная панель для адресов пользователей"""
    
    list_display = (
        'user', 'city', 'state', 'country', 
        'get_full_address_display', 'get_user_email', 'get_user_name'
    )
    list_filter = (
        'country', 'state', 'city', 'user__is_active', 'user__date_joined'
    )
    search_fields = (
        'user__email', 'user__name', 'city', 'state', 
        'address_line', 'postal_code', 'country'
    )
    ordering = ('city',)
    list_display_links = ('user', 'city')
    
    # Поля для поиска по связанным моделям
    raw_id_fields = ('user',)
    
    # Поля для редактирования
    fieldsets = (
        (_('Пользователь'), {
            'fields': ('user',)
        }),
        (_('Адрес'), {
            'fields': ('address_line', 'city', 'state', 'postal_code', 'country')
        }),
    )
    
    @admin.display(description=_('Полный адрес'))
    def get_full_address_display(self, obj):
        """Возвращает полный адрес для отображения"""
        address = obj.get_full_address()
        if len(address) > 50:
            return format_html(
                '<span title="{}">{}</span>',
                address,
                address[:50] + '...'
            )
        return address
    
    @admin.display(description=_('Email пользователя'))
    def get_user_email(self, obj):
        """Возвращает email пользователя"""
        return obj.user.email
    
    @admin.display(description=_('Имя пользователя'))
    def get_user_name(self, obj):
        """Возвращает имя пользователя"""
        return obj.user.get_full_name() or '-'
