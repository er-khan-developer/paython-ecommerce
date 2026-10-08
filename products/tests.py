from django.test import TestCase
from django.urls import reverse

from .models import Category, Product


class CategoryTests(TestCase):
    def test_product_can_use_a_subcategory(self):
        parent = Category.objects.create(name='Clothing')
        subcategory = Category.objects.create(name='Shirts', parent=parent)
        product = Product.objects.create(
            name='Oxford shirt',
            description='Cotton shirt',
            price='29.99',
            category=subcategory,
        )

        self.assertEqual(subcategory.parent, parent)
        self.assertEqual(parent.subcategories.get(), subcategory)
        self.assertEqual(product.category, subcategory)

    def test_home_renders_category_accordion_and_subcategory_ajax_controls(self):
        parent = Category.objects.create(name='Clothing')
        subcategory = Category.objects.create(name='Shirts', parent=parent)

        response = self.client.get(reverse('home'))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, f'data-category-id="{parent.id}"')
        self.assertContains(response, f'data-subcategory-id="{subcategory.id}"')
        self.assertContains(response, 'data-bs-toggle="collapse"')
        self.assertContains(response, 'data-filter-url="/products/filter/"')
        self.assertContains(response, 'class="col-lg-3 col-xl-2 catalog-sidebar"')
        self.assertContains(response, 'category-sidebar-toggle')
        self.assertContains(response, 'data-bs-target="#category-sidebar-content"')

    def test_home_paginates_products(self):
        for index in range(13):
            Product.objects.create(
                name=f'Product {index + 1}',
                description='Test product',
                price='10.00',
            )

        response = self.client.get(reverse('home'))

        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.context['products']), 12)
        self.assertEqual(response.context['products'].paginator.count, 13)
        self.assertContains(response, 'aria-label="Product pagination"')

        second_page = self.client.get(reverse('home'), {'page': 2})
        self.assertEqual(len(second_page.context['products']), 1)


class CategoryFilterAjaxTests(TestCase):
    def setUp(self):
        self.parent = Category.objects.create(name='Clothing')
        self.subcategory = Category.objects.create(name='Shirts', parent=self.parent)
        self.other_subcategory = Category.objects.create(name='Pants', parent=self.parent)
        self.product = Product.objects.create(
            name='Oxford shirt',
            description='Cotton shirt',
            price='29.99',
            category=self.subcategory,
        )
        Product.objects.create(
            name='Cargo pants',
            description='Cotton pants',
            price='49.99',
            category=self.other_subcategory,
        )

    def test_filter_returns_child_categories_and_matching_products(self):
        response = self.client.get(
            reverse('product_filter'),
            {'category_id': self.parent.id, 'subcategory_id': self.subcategory.id},
            HTTP_X_REQUESTED_WITH='XMLHttpRequest',
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.headers['Content-Type'], 'application/json')
        self.assertEqual(response.json()['category_label'], 'Clothing')
        self.assertEqual(len(response.json()['subcategories']), 2)
        self.assertIn('Oxford shirt', response.json()['products_html'])
        self.assertNotIn('Cargo pants', response.json()['products_html'])

    def test_filter_without_selection_returns_all_available_products(self):
        response = self.client.get(
            reverse('product_filter'),
            HTTP_X_REQUESTED_WITH='XMLHttpRequest',
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()['products_count'], 2)
        self.assertIn('Oxford shirt', response.json()['products_html'])
        self.assertIn('Cargo pants', response.json()['products_html'])
