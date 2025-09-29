from django.contrib.auth.models import AbstractUser, BaseUserManager
from django.db import models
from django.utils.translation import gettext_lazy as _

class UserManager(BaseUserManager):
    use_in_migrations = True
    
    def _create_user(self, email, password, **extra_fields):
        if not email:
            raise ValueError(_("Email обязателен"))
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user
    
    def create_user(self, email, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', False)
        extra_fields.setdefault('is_superuser', False)
        return self._create_user(email, password, **extra_fields)
    
    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        return self._create_user(email, password, **extra_fields)

class User(AbstractUser):
    """Модель пользователя системы"""
    
    username = None
    email = models.EmailField(
        verbose_name=_("Email адрес"),
        unique=True,
        help_text=_("Используется для входа в систему")
    )
    name = models.CharField(
        verbose_name=_("Имя"),
        max_length=120,
        blank=True,  # Необязательное поле - пользователь может не указать имя
        help_text=_("Полное имя пользователя")
    )
    phone = models.CharField(
        verbose_name=_("Телефон"),
        max_length=20,
        blank=True,  # Необязательное поле - пользователь может не указать телефон
        help_text=_("Номер телефона для связи")
    )
    ROLE_CHOICES = (
        ('customer', 'Customer'),
        ('admin', 'Admin'),
    )
    role = models.CharField('Роль', max_length=20, choices=ROLE_CHOICES, default='customer')
    
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []
    
    objects = UserManager()

    class Meta:
        verbose_name = _("Пользователь")
        verbose_name_plural = _("Пользователи")
        ordering = ['-date_joined']
        db_table = 'accounts_user'

    def __str__(self):
        if self.name:
            return f"{self.name} ({self.email})"
        return self.email

    def get_full_name(self):
        """Возвращает полное имя пользователя"""
        if self.name:
            return self.name
        return self.email

    def get_short_name(self):
        """Возвращает короткое имя пользователя"""
        if self.name:
            return self.name.split()[0] if ' ' in self.name else self.name
        return self.email.split('@')[0]

class UserAddress(models.Model):
    """Модель адреса доставки пользователя"""
    
    address_line = models.CharField(
        verbose_name=_("Адрес"),
        max_length=255,
        blank=True,  # Необязательное поле - может быть указан только город
        null=True,
        help_text=_("Улица, дом, квартира")
    )
    city = models.CharField(
        verbose_name=_("Город"),
        max_length=100,
        blank=True,  # Необязательное поле - пользователь может не указать город
        null=True,
        help_text=_("Название города")
    )
    state = models.CharField(
        verbose_name=_("Область/Регион"),
        max_length=100,
        blank=True,  # Необязательное поле - может быть не указана
        null=True,
        help_text=_("Название области или региона")
    )
    postal_code = models.CharField(
        verbose_name=_("Почтовый индекс"),
        max_length=20,
        blank=True,  # Необязательное поле - может быть не указан
        null=True,
        help_text=_("Почтовый индекс")
    )
    country = models.CharField(
        verbose_name=_("Страна"),
        max_length=100,
        default="Россия",
        help_text=_("Название страны")
    )
    user = models.ForeignKey(
        User,
        verbose_name=_("Пользователь"),
        on_delete=models.CASCADE,
        related_name="addresses"
    )

    class Meta:
        verbose_name = _("Адрес доставки")
        verbose_name_plural = _("Адреса доставки")
        ordering = ['city']
        db_table = 'accounts_useraddress'

    def __str__(self):
        if self.city and self.address_line:
            return f"{self.city}, {self.address_line}"
        elif self.city:
            return f"{self.city}, {self.country}"
        return f"Адрес {self.user.email}"

    def get_full_address(self):
        """Возвращает полный адрес"""
        parts = []
        if self.address_line:
            parts.append(self.address_line)
        if self.city:
            parts.append(self.city)
        if self.state:
            parts.append(self.state)
        if self.postal_code:
            parts.append(self.postal_code)
        if self.country:
            parts.append(self.country)
        return ", ".join(parts)
