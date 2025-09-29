from django.test import TestCase, Client
from django.urls import reverse
from catalog.models import Product, Category

class CatalogViewsTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.category = Category.objects.create(name="Cat", slug="cat")
        self.product = Product.objects.create(name="Prod", category=self.category, base_price=100.0)

    def test_home_view(self):
        response = self.client.get(reverse("home"))  # Замените на ваше имя url
        self.assertEqual(response.status_code, 200)
        self.assertIn('products', response.context)

    def test_product_detail_view(self):
        response = self.client.get(reverse("product_detail", args=[self.product.pk]))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context['product'], self.product)
