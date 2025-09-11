from django.db import models
from django.utils.translation import gettext_lazy as _
from decimal import Decimal
from accounts.models import User
from catalog.models import ProductVariant

ORDER_STATUS = (
    ('pending', _('Ожидает подтверждения')),
    ('placed', _('Размещен')),
    ('processing', _('В обработке')),
    ('out_for_delivery', _('Отправлен')),
    ('shipped', _('Доставляется')),
    ('delivered', _('Доставлен')),
    ('cancelled', _('Отменен')),
    ('refunded', _('Возвращен')),
)

PAYMENT_STATUS = (
    ('pending', _('Ожидает оплаты')),
    ('paid', _('Оплачен')),
    ('failed', _('Ошибка оплаты')),
    ('refunded', _('Возвращен')),
)

PAYMENT_METHOD = (
    ('card', _('Банковская карта')),
    ('cash', _('Наличные при получении')),
    ('online', _('Онлайн оплата')),
    ('bank_transfer', _('Банковский перевод')),
)

class Coupon(models.Model):
    """Модель купона для скидок"""
    
    code = models.CharField(
        verbose_name=_("Код купона"),
        max_length=50,
        unique=True,
        help_text=_("Уникальный код купона")
    )
    name = models.CharField(
        verbose_name=_("Название"),
        max_length=100,
        help_text=_("Название купона")
    )
    description = models.TextField(
        verbose_name=_("Описание"),
        blank=True,
        help_text=_("Описание купона")
    )
    discount_percent = models.PositiveIntegerField(
        verbose_name=_("Процент скидки"),
        default=0,
        help_text=_("Процент скидки (например, 10 для 10%)")
    )
    discount_amount = models.DecimalField(
        verbose_name=_("Сумма скидки"),
        max_digits=10,
        decimal_places=2,
        default=0,
        help_text=_("Фиксированная сумма скидки")
    )
    min_order_amount = models.DecimalField(
        verbose_name=_("Минимальная сумма заказа"),
        max_digits=10,
        decimal_places=2,
        default=0,
        help_text=_("Минимальная сумма для применения купона")
    )
    max_uses = models.PositiveIntegerField(
        verbose_name=_("Максимум использований"),
        blank=True,
        null=True,
        help_text=_("Максимальное количество использований")
    )
    used_count = models.PositiveIntegerField(
        verbose_name=_("Количество использований"),
        default=0,
        help_text=_("Сколько раз уже использован купон")
    )
    active = models.BooleanField(
        verbose_name=_("Активен"),
        default=True,
        help_text=_("Действует ли купон")
    )
    valid_from = models.DateTimeField(
        verbose_name=_("Действует с"),
        blank=True,
        null=True,
        help_text=_("Дата начала действия купона")
    )
    valid_until = models.DateTimeField(
        verbose_name=_("Действует до"),
        blank=True,
        null=True,
        help_text=_("Дата окончания действия купона")
    )
    created_at = models.DateTimeField(
        verbose_name=_("Дата создания"),
        auto_now_add=True
    )
    updated_at = models.DateTimeField(
        verbose_name=_("Дата обновления"),
        auto_now=True
    )

    class Meta:
        verbose_name = _("Купон")
        verbose_name_plural = _("Купоны")
        ordering = ['-created_at']
        db_table = 'orders_coupon'

    def __str__(self):
        return f"{self.name} ({self.code})"

    def apply(self, amount):
        """Применяет купон к сумме"""
        if not self.active:
            return Decimal('0.00')
        
        if amount < self.min_order_amount:
            return Decimal('0.00')
        
        if self.discount_percent > 0:
            return (Decimal(self.discount_percent) / Decimal('100')) * amount
        elif self.discount_amount > 0:
            return min(self.discount_amount, amount)
        
        return Decimal('0.00')

    def can_use(self):
        """Проверяет, можно ли использовать купон"""
        if not self.active:
            return False
        
        if self.max_uses and self.used_count >= self.max_uses:
            return False
        
        return True

    def increment_usage(self):
        """Увеличивает счетчик использований"""
        self.used_count += 1
        self.save()

class Order(models.Model):
    """Модель заказа"""
    
    order_number = models.CharField(
        verbose_name=_("Номер заказа"),
        max_length=20,
        unique=True,
        help_text=_("Уникальный номер заказа")
    )
    user = models.ForeignKey(
        User,
        verbose_name=_("Пользователь"),
        on_delete=models.CASCADE,
        related_name='orders',
        help_text=_("Покупатель")
    )
    status = models.CharField(
        verbose_name=_("Статус заказа"),
        max_length=20,
        choices=ORDER_STATUS,
        default='pending',
        help_text=_("Текущий статус заказа")
    )
    payment_status = models.CharField(
        verbose_name=_("Статус оплаты"),
        max_length=20,
        choices=PAYMENT_STATUS,
        default='pending',
        help_text=_("Статус оплаты заказа")
    )
    payment_method = models.CharField(
        verbose_name=_("Способ оплаты"),
        max_length=20,
        choices=PAYMENT_METHOD,
        default='card',
        help_text=_("Выбранный способ оплаты")
    )
    tracking_number = models.CharField(
        verbose_name=_("Номер отслеживания"),
        max_length=100,
        blank=True,
        help_text=_("Номер для отслеживания доставки")
    )
    coupon = models.ForeignKey(
        Coupon,
        verbose_name=_("Купон"),
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        help_text=_("Примененный купон")
    )
    subtotal = models.DecimalField(
        verbose_name=_("Сумма без скидки"),
        max_digits=12,
        decimal_places=2,
        default=0,
        help_text=_("Сумма товаров без учета скидки")
    )
    discount_amount = models.DecimalField(
        verbose_name=_("Сумма скидки"),
        max_digits=12,
        decimal_places=2,
        default=0,
        help_text=_("Сумма скидки по купону")
    )
    shipping_cost = models.DecimalField(
        verbose_name=_("Стоимость доставки"),
        max_digits=10,
        decimal_places=2,
        default=0,
        help_text=_("Стоимость доставки")
    )
    total_amount = models.DecimalField(
        verbose_name=_("Итоговая сумма"),
        max_digits=12,
        decimal_places=2,
        default=0,
        help_text=_("Итоговая сумма заказа")
    )
    address = models.TextField(
        verbose_name=_("Адрес доставки"),
        blank=True,
        null=True,
        help_text=_("Полный адрес доставки")
    )
    phone = models.CharField(
        verbose_name=_("Телефон"),
        max_length=20,
        blank=True,
        help_text=_("Контактный телефон")
    )
    notes = models.TextField(
        verbose_name=_("Примечания"),
        blank=True,
        help_text=_("Дополнительные примечания к заказу")
    )
    estimated_delivery = models.DateField(
        verbose_name=_("Ожидаемая дата доставки"),
        blank=True,
        null=True,
        help_text=_("Предполагаемая дата доставки")
    )
    delivered_at = models.DateTimeField(
        verbose_name=_("Дата доставки"),
        blank=True,
        null=True,
        help_text=_("Фактическая дата доставки")
    )
    created_at = models.DateTimeField(
        verbose_name=_("Дата создания"),
        auto_now_add=True
    )
    updated_at = models.DateTimeField(
        verbose_name=_("Дата обновления"),
        auto_now=True
    )

    class Meta:
        verbose_name = _("Заказ")
        verbose_name_plural = _("Заказы")
        ordering = ['-created_at']
        db_table = 'orders_order'

    def __str__(self):
        return f"Заказ {self.order_number} - {self.user.get_short_name()}"

    def save(self, *args, **kwargs):
        """Автоматически генерирует номер заказа"""
        if not self.order_number:
            self.order_number = self.generate_order_number()
        super().save(*args, **kwargs)

    def generate_order_number(self):
        """Генерирует уникальный номер заказа"""
        import random
        import string
        from datetime import datetime
        
        timestamp = datetime.now().strftime('%Y%m%d%H%M%S')
        random_chars = ''.join(random.choices(string.ascii_uppercase + string.digits, k=6))
        return f"ORD-{timestamp}-{random_chars}"

    def get_status_display_ru(self):
        """Возвращает статус на русском языке"""
        return dict(ORDER_STATUS).get(self.status, self.status)

    def get_payment_status_display_ru(self):
        """Возвращает статус оплаты на русском языке"""
        return dict(PAYMENT_STATUS).get(self.payment_status, self.payment_status)

    def calculate_totals(self):
        """Пересчитывает итоговые суммы"""
        self.subtotal = sum(item.subtotal for item in self.items.all())
        
        if self.coupon:
            self.discount_amount = self.coupon.apply(self.subtotal)
        else:
            self.discount_amount = Decimal('0.00')
        
        self.total_amount = self.subtotal - self.discount_amount + self.shipping_cost
        self.save()

    def get_items_count(self):
        """Возвращает количество товаров в заказе"""
        return self.items.count()

    def get_total_quantity(self):
        """Возвращает общее количество товаров"""
        return sum(item.quantity for item in self.items.all())

    def can_cancel(self):
        """Проверяет, можно ли отменить заказ"""
        return self.status in ['pending', 'placed', 'processing']

    def cancel(self):
        """Отменяет заказ"""
        if self.can_cancel():
            self.status = 'cancelled'
            self.save()
            return True
        return False

class OrderItem(models.Model):
    """Модель товара в заказе"""
    
    order = models.ForeignKey(
        Order,
        verbose_name=_("Заказ"),
        on_delete=models.CASCADE,
        related_name='items',
        help_text=_("Заказ, в котором находится товар")
    )
    variant = models.ForeignKey(
        ProductVariant,
        verbose_name=_("Вариант товара"),
        on_delete=models.PROTECT,
        related_name='order_items',
        help_text=_("Заказанный вариант товара")
    )
    quantity = models.PositiveIntegerField(
        verbose_name=_("Количество"),
        default=1,
        help_text=_("Заказанное количество")
    )
    price = models.DecimalField(
        verbose_name=_("Цена"),
        max_digits=10,
        decimal_places=2,
        help_text=_("Цена на момент заказа")
    )
    created_at = models.DateTimeField(
        verbose_name=_("Дата создания"),
        auto_now_add=True
    )

    class Meta:
        verbose_name = _("Товар в заказе")
        verbose_name_plural = _("Товары в заказах")
        ordering = ['order', 'created_at']
        db_table = 'orders_orderitem'

    def __str__(self):
        return f"{self.variant.product.name} ({self.variant.get_display_name()}) x{self.quantity}"

    @property
    def subtotal(self):
        """Возвращает стоимость товара с учетом количества"""
        return self.price * self.quantity

    def get_product_name(self):
        """Возвращает название товара"""
        return self.variant.product.name

    def get_variant_display(self):
        """Возвращает отображение варианта"""
        return self.variant.get_display_name()

    def get_current_price(self):
        """Возвращает текущую цену товара"""
        return self.variant.price
