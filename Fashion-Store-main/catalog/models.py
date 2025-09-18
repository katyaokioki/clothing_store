from django.db import models
from django.urls import reverse
from django.utils.translation import gettext_lazy as _
from accounts.models import User

class Category(models.Model):
    """Модель категории товаров"""
    
    name = models.CharField(
        verbose_name=_("Название"),
        max_length=100,
        help_text=_("Название категории товаров")
    )
    slug = models.SlugField(
        verbose_name=_("URL-идентификатор"),
        unique=True,
        help_text=_("Уникальный идентификатор для URL")
    )
    description = models.TextField(
        verbose_name=_("Описание"),
        blank=True,
        help_text=_("Описание категории")
    )
    image = models.ImageField(
        verbose_name=_("Изображение"),
        upload_to='categories/',
        blank=True,
        null=True,
        help_text=_("Изображение категории")
    )
    is_active = models.BooleanField(
        verbose_name=_("Активна"),
        default=True,
        help_text=_("Показывать ли категорию на сайте")
    )
    sort_order = models.PositiveIntegerField(
        verbose_name=_("Порядок сортировки"),
        default=0,
        help_text=_("Порядок отображения категории")
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
        verbose_name = _("Категория")
        verbose_name_plural = _("Категории")
        ordering = ['sort_order', 'name']
        db_table = 'catalog_category'

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse('product_list') + f'?category={self.slug}'

    def get_products_count(self):
        """Возвращает количество товаров в категории"""
        return self.products.count()

class OtherCategory(models.Model):
    """Модель дополнительной категории товаров"""
    
    name = models.CharField(
        verbose_name=_("Название"),
        max_length=100,
        help_text=_("Название дополнительной категории")
    )
    slug = models.SlugField(
        verbose_name=_("URL-идентификатор"),
        unique=True,
        help_text=_("Уникальный идентификатор для URL")
    )
    description = models.TextField(
        verbose_name=_("Описание"),
        blank=True,
        help_text=_("Описание дополнительной категории")
    )
    is_active = models.BooleanField(
        verbose_name=_("Активна"),
        default=True,
        help_text=_("Показывать ли категорию на сайте")
    )
    created_at = models.DateTimeField(
        verbose_name=_("Дата создания"),
        auto_now_add=True
    )

    class Meta:
        verbose_name = _("Дополнительная категория")
        verbose_name_plural = _("Дополнительные категории")
        ordering = ['name']
        db_table = 'catalog_othercategory'

    def __str__(self):
        return self.name

        
class Collection(models.Model):
    name = models.CharField(max_length=120)
    slug = models.SlugField(unique=True)
    def __str__(self):
        return self.name


class ProductCollection(models.Model):
    product = models.ForeignKey('catalog.Product', on_delete=models.CASCADE, related_name='product_collections')
    collection = models.ForeignKey(Collection, on_delete=models.CASCADE, related_name='collection_products')
    order = models.PositiveIntegerField(default=0, help_text="Порядок внутри подборки")
    featured_until = models.DateTimeField(blank=True, null=True, help_text="Дата, до которой товар выделен")
    added_at = models.DateTimeField(auto_now_add=True)
    class Meta:
        unique_together = ('product', 'collection')
        ordering = ['collection', 'order']

    def __str__(self):
        return f'{self.collection.name} — {self.product.name} (#{self.order})'


class Product(models.Model):
    """Модель товара"""
    
    name = models.CharField(
        verbose_name=_("Название"),
        max_length=200,
        help_text=_("Название товара")
    )
    description = models.TextField(
        verbose_name=_("Описание"),
        blank=True,
        help_text=_("Подробное описание товара")
    )
    short_description = models.CharField(
        verbose_name=_("Краткое описание"),
        max_length=255,
        blank=True,
        help_text=_("Краткое описание для списка товаров")
    )
    base_price = models.DecimalField(
        verbose_name=_("Базовая цена"),
        max_digits=10,
        decimal_places=2,
        help_text=_("Базовая цена товара")
    )
    sale_price = models.DecimalField(
        verbose_name=_("Цена со скидкой"),
        max_digits=10,
        decimal_places=2,
        blank=True,
        null=True,
        help_text=_("Цена товара со скидкой")
    )
    image = models.ImageField(
        verbose_name=_("Основное изображение"),
        upload_to='products/',
        blank=True,
        null=True,
        help_text=_("Главное изображение товара")
    )
    category = models.ForeignKey(
        Category,
        verbose_name=_("Категория"),
        on_delete=models.CASCADE,
        related_name='products',
        help_text=_("Основная категория товара")
    )
    other_category = models.ForeignKey(
        OtherCategory,
        verbose_name=_("Дополнительная категория"),
        on_delete=models.CASCADE,
        related_name='other_products',
        blank=True,
        null=True,
        help_text=_("Дополнительная категория товара")
    )
    is_active = models.BooleanField(
        verbose_name=_("Активен"),
        default=True,
        help_text=_("Показывать ли товар на сайте")
    )
    is_featured = models.BooleanField(
        verbose_name=_("Рекомендуемый"),
        default=False,
        help_text=_("Показывать ли товар в рекомендуемых")
    )
    is_new = models.BooleanField(
        verbose_name=_("Новинка"),
        default=False,
        help_text=_("Показывать ли товар как новинку")
    )
    weight = models.DecimalField(
        verbose_name=_("Вес"),
        max_digits=6,
        decimal_places=2,
        blank=True,
        null=True,
        help_text=_("Вес товара в граммах")
    )
    dimensions = models.CharField(
        verbose_name=_("Размеры"),
        max_length=100,
        blank=True,
        help_text=_("Размеры товара (ДxШxВ)")
    )
    created_at = models.DateTimeField(
        verbose_name=_("Дата создания"),
        auto_now_add=True
    )
    updated_at = models.DateTimeField(
        verbose_name=_("Дата обновления"),
        auto_now=True
    )

    collections = models.ManyToManyField(
        Collection,
        through='ProductCollection',
        related_name='products',
        blank=True,
        )

    class Meta:
        verbose_name = _("Товар")
        verbose_name_plural = _("Товары")
        ordering = ['-created_at']
        db_table = 'catalog_product'

    def __str__(self):
        return f"{self.name} - {self.category.name}"

    def get_absolute_url(self):
        return reverse('product_detail', args=[self.id])

    def get_current_price(self):
        """Возвращает текущую цену товара"""
        return self.sale_price if self.sale_price else self.base_price

    def get_discount_percent(self):
        """Возвращает процент скидки"""
        if self.sale_price and self.base_price > self.sale_price:
            return int(((self.base_price - self.sale_price) / self.base_price) * 100)
        return 0

    def get_variants_count(self):
        """Возвращает количество вариантов товара"""
        return self.variants.count()

    def get_total_stock(self):
        """Возвращает общий остаток на складе"""
        return sum(variant.stock for variant in self.variants.all())

    def get_average_rating(self):
        """Возвращает средний рейтинг товара"""
        reviews = self.reviews.all()
        if reviews:
            return sum(review.rating for review in reviews) / len(reviews)
        return 0

    def get_reviews_count(self):
        """Возвращает количество отзывов"""
        return self.reviews.count()

class ProductVariant(models.Model):
    """Модель варианта товара"""
    
    product = models.ForeignKey(
        Product,
        verbose_name=_("Товар"),
        on_delete=models.CASCADE,
        related_name='variants',
        help_text=_("Основной товар")
    )
    size = models.CharField(
        verbose_name=_("Размер"),
        max_length=20,
        help_text=_("Размер товара")
    )
    color = models.CharField(
        verbose_name=_("Цвет"),
        max_length=30,
        help_text=_("Цвет товара")
    )
    price = models.DecimalField(
        verbose_name=_("Цена"),
        max_digits=10,
        decimal_places=2,
        help_text=_("Цена варианта товара")
    )
    stock = models.PositiveIntegerField(
        verbose_name=_("Остаток на складе"),
        default=0,
        help_text=_("Количество товара на складе")
    )
    image = models.ImageField(
        verbose_name=_("Изображение"),
        upload_to='products/',
        blank=True,
        null=True,
        help_text=_("Изображение варианта товара")
    )
    sku = models.CharField(
        verbose_name=_("Артикул"),
        max_length=50,
        unique=True,
        blank=True,
        null=True,
        help_text=_("Уникальный артикул варианта")
    )
    is_active = models.BooleanField(
        verbose_name=_("Активен"),
        default=True,
        help_text=_("Показывать ли вариант на сайте")
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
        verbose_name = _("Вариант товара")
        verbose_name_plural = _("Варианты товаров")
        unique_together = ('product', 'size', 'color')
        ordering = ['product', 'size', 'color']
        db_table = 'catalog_productvariant'

    def __str__(self):
        return f"{self.product.name} - {self.size}/{self.color}"

    def get_display_name(self):
        """Возвращает отображаемое название варианта"""
        return f"{self.size} / {self.color}"

    def is_in_stock(self):
        """Проверяет, есть ли товар в наличии"""
        return self.stock > 0

    def get_stock_status(self):
        """Возвращает статус наличия товара"""
        if self.stock == 0:
            return "Нет в наличии"
        elif self.stock <= 5:
            return "Заканчивается"
        else:
            return "В наличии"

class Review(models.Model):
    """Модель отзыва о товаре"""
    
    RATING_CHOICES = [
        (1, _('1 звезда')),
        (2, _('2 звезды')),
        (3, _('3 звезды')),
        (4, _('4 звезды')),
        (5, _('5 звезд')),
    ]
    
    product = models.ForeignKey(
        Product,
        verbose_name=_("Товар"),
        on_delete=models.CASCADE,
        related_name='reviews',
        help_text=_("Товар, к которому относится отзыв")
    )
    user = models.ForeignKey(
        User,
        verbose_name=_("Пользователь"),
        on_delete=models.CASCADE,
        help_text=_("Автор отзыва")
    )
    rating = models.PositiveIntegerField(
        verbose_name=_("Оценка"),
        choices=RATING_CHOICES,
        default=5,
        help_text=_("Оценка товара от 1 до 5")
    )
    comment = models.TextField(
        verbose_name=_("Комментарий"),
        blank=True,
        help_text=_("Текст отзыва")
    )
    is_approved = models.BooleanField(
        verbose_name=_("Одобрен"),
        default=False,
        help_text=_("Одобрен ли отзыв модератором")
    )
    is_verified_purchase = models.BooleanField(
        verbose_name=_("Подтвержденная покупка"),
        default=False,
        help_text=_("Покупал ли пользователь этот товар")
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
        verbose_name = _("Отзыв")
        verbose_name_plural = _("Отзывы")
        unique_together = ('product', 'user')
        ordering = ['-created_at']
        db_table = 'catalog_review'

    def __str__(self):
        return f"Отзыв {self.user.get_short_name()} о {self.product.name}"

    def get_rating_display(self):
        """Возвращает отображаемую оценку"""
        return "★" * self.rating

class ReviewImage(models.Model):
    """Модель изображения в отзыве"""
    
    image = models.ImageField(
        verbose_name=_("Изображение"),
        upload_to='reviews_images/',
        blank=True,
        null=True,
        help_text=_("Изображение к отзыву")
    )
    review = models.ForeignKey(
        Review,
        verbose_name=_("Отзыв"),
        on_delete=models.CASCADE,
        blank=True,
        null=True,
        related_name='reviews_image',
        help_text=_("Отзыв, к которому относится изображение")
    )
    alt_text = models.CharField(
        verbose_name=_("Альтернативный текст"),
        max_length=255,
        blank=True,
        help_text=_("Описание изображения для SEO")
    )
    created_at = models.DateTimeField(
        verbose_name=_("Дата создания"),
        auto_now_add=True
    )

    class Meta:
        verbose_name = _("Изображение отзыва")
        verbose_name_plural = _("Изображения отзывов")
        ordering = ['-created_at']
        db_table = 'catalog_reviewimage'

    def __str__(self):
        if self.review:
            return f"Изображение к отзыву {self.review.id}"
        return f"Изображение {self.id}"



