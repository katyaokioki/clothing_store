from django.db import models
from django.utils.translation import gettext_lazy as _
from accounts.models import User
from catalog.models import ProductVariant

class Cart(models.Model):
    """Модель корзины пользователя"""
    
    user = models.OneToOneField(
        User,
        verbose_name=_("Пользователь"),
        on_delete=models.CASCADE,
        related_name='cart',
        help_text=_("Владелец корзины")
    )
    coupon_code = models.CharField(
        verbose_name=_("Код купона"),
        max_length=50,
        blank=True,
        default='',
        help_text=_("Примененный код купона")
    )

    class Meta:
        verbose_name = _("Корзина")
        verbose_name_plural = _("Корзины")
        db_table = 'cart_cart'

    def __str__(self):
        return f"Корзина {self.user.get_short_name()}"

    def get_items_count(self):
        """Возвращает количество товаров в корзине"""
        return self.items.count()

    def get_total_quantity(self):
        """Возвращает общее количество товаров"""
        return sum(item.quantity for item in self.items.all())

    def get_subtotal(self):
        """Возвращает сумму без скидки"""
        return sum(item.subtotal for item in self.items.all())

    def get_discount_amount(self):
        """Возвращает сумму скидки"""
        from orders.models import Coupon
        if self.coupon_code:
            try:
                coupon = Coupon.objects.get(code__iexact=self.coupon_code, active=True)
                return coupon.apply(self.get_subtotal())
            except Coupon.DoesNotExist:
                return 0
        return 0

    def get_total(self):
        """Возвращает итоговую сумму с учетом скидки"""
        subtotal = self.get_subtotal()
        discount = self.get_discount_amount()
        return max(0, subtotal - discount)

    def is_empty(self):
        """Проверяет, пуста ли корзина"""
        return self.items.count() == 0

    def clear(self):
        """Очищает корзину"""
        self.items.all().delete()
        self.coupon_code = ''
        self.save()

class CartItem(models.Model):
    """Модель товара в корзине"""
    
    cart = models.ForeignKey(
        Cart,
        verbose_name=_("Корзина"),
        on_delete=models.CASCADE,
        related_name='items',
        help_text=_("Корзина, в которой находится товар")
    )
    variant = models.ForeignKey(
        ProductVariant,
        verbose_name=_("Вариант товара"),
        on_delete=models.CASCADE,
        help_text=_("Выбранный вариант товара")
    )
    quantity = models.PositiveIntegerField(
        verbose_name=_("Количество"),
        default=1,
        help_text=_("Количество товара")
    )

    class Meta:
        verbose_name = _("Товар в корзине")
        verbose_name_plural = _("Товары в корзине")
        unique_together = ('cart', 'variant')
        db_table = 'cart_cartitem'

    def __str__(self):
        return f"{self.variant.product.name} ({self.variant.get_display_name()}) x{self.quantity}"

    @property
    def subtotal(self):
        """Возвращает стоимость товара с учетом количества"""
        return self.variant.price * self.quantity

    def get_product_name(self):
        """Возвращает название товара"""
        return self.variant.product.name

    def get_variant_display(self):
        """Возвращает отображение варианта"""
        return self.variant.get_display_name()

    def get_unit_price(self):
        """Возвращает цену за единицу"""
        return self.variant.price

    def can_increase_quantity(self):
        """Проверяет, можно ли увеличить количество"""
        return self.quantity < self.variant.stock

    def increase_quantity(self, amount=1):
        """Увеличивает количество товара"""
        if self.can_increase_quantity():
            self.quantity += amount
            self.save()
            return True
        return False

    def decrease_quantity(self, amount=1):
        """Уменьшает количество товара"""
        if self.quantity > amount:
            self.quantity -= amount
            self.save()
            return True
        elif self.quantity == amount:
            self.delete()
            return True
        return False
