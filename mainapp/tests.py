from decimal import Decimal
from unittest import mock

from django.contrib.auth import get_user_model
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import RequestFactory, TestCase

from .models import Cart, CartProduct, Category, Customer, Notebook
from .views import AddToCartView, BaseView, recalc_cart

User = get_user_model()


class StoreTestCases(TestCase):
    def setUp(self) -> None:
        self.user = User.objects.create(username="testuser", password="password")
        self.category = Category.objects.create(name="Ноутбуки", slug="notebooks")
        image = SimpleUploadedFile(
            "notebook_image.jpg", content=b"", content_type="image/jpg"
        )
        self.notebook = Notebook.objects.create(
            category=self.category,
            title="Test Notebook",
            slug="test-slug",
            image=image,
            price=Decimal("50000"),
            diagonal="17.3",
            display_type="IPS",
            processor_freq="3.4 GHz",
            ram="6 GB",
            video_card="GeForce GTX 1050ti",
            time_without_charge="8 hours",
        )
        self.customer = Customer.objects.create(
            user=self.user, phone="+79097524578", address="jgweiro hghiorroeg"
        )
        self.cart = Cart.objects.create(owner=self.customer)
        self.cart_product = CartProduct.objects.create(
            user=self.customer, cart=self.cart, content_object=self.notebook
        )
        return super().setUp()

    def test_add_to_cart(self):
        self.cart.products.add(self.cart_product)
        recalc_cart(self.cart)
        self.assertIn(self.cart_product, self.cart.products.all())
        self.assertEqual(self.cart.products.count(), 1)
        self.assertEqual(self.cart.final_price, Decimal("50000"))

    def test_response_from_add_to_cart_view(self):
        factory = RequestFactory()
        request = factory.get("")
        request.user = self.user
        response = AddToCartView.as_view()(
            request, ct_model="notebook", slug="test-slug"
        )
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, "/cart/")

    def test_mock_homepage(self):
        mock_data = mock.Mock(status_code=444)
        with mock.patch(
            "mainapp.views.BaseView.get", return_value=mock_data
        ) as mock_data:
            factory = RequestFactory()
            request = factory.get("")
            request.user = self.user
            response = BaseView.as_view()(request)
            self.assertEqual(response.status_code, 444)
