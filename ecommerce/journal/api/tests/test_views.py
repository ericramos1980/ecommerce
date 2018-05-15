from decimal import Decimal as D

import simplejson as json
from django.urls import reverse
from oscar.core.loading import get_model

from ecommerce.tests.testcases import TestCase

Product = get_model('catalogue', 'Product')
Partner = get_model('partner', 'Partner')


class JournalProductViewTests(TestCase):

    def setUp(self):
        """
        Creates the sample data for test cases.
        """
        super(JournalProductViewTests, self).setUp()
        user = self.create_user(is_staff=True)
        self.client.login(username=user.username, password=self.password)

        self.value_text = "dummy_text"
        self.path = reverse("journal:api:v1:journal-list")
        self.product = self._create_product()

    def _create_product(self):
        self.client.post(self.path, json.dumps(self._get_data_for_create()), "application/json")
        return Product.objects.first()

    def _get_product(self):
        path = reverse(
            'journal:api:v1:journal-detail',
            kwargs={'attribute_values__value_text': self.value_text}
        )
        response = self.client.get(path)
        return json.loads(response.content)

    def _get_data_for_create(self):
        return {
            'attribute_values': [
                {'code': 'weight', 'name': 'weight', 'value': self.value_text}
            ],
            'stockrecords': [
                {
                    'partner': 'edx',
                    'partner_sku': 'unit02',
                    'price_excl_tax': '9.99',
                    'price_currency': 'GBP'
                }
            ],
            'product_class': 'Journal',
            'title': 'dummy-product-title',
            'expires': None,
            'id': None,
            'structure': 'standalone'
        }

    def _get_data_for_put_endpoint(self):
        """
        Returns the data to be updated for product.
        """

        return {
            "title": "changed-product-title",
            "stockrecords": [
                {
                    "price_excl_tax": D('1.02'),
                    "price_currency": "USD"
                },
                {
                    "price_excl_tax": D('1.02'),
                    "price_currency": "USD"
                }
            ]
        }

    def _assert_product_update(self):
        """
        Asserts the updated product values.
        """
        product = self._get_product()
        expected_data = self._get_data_for_put_endpoint()
        self.assertEqual(product['title'], expected_data['title'])
        for index, stockrecord in enumerate(product['stockrecords']):
            self.assertEqual(
                stockrecord['price_excl_tax'],
                str(expected_data['stockrecords'][index]['price_excl_tax'])
            )
            self.assertEqual(
                stockrecord['price_currency'],
                expected_data['stockrecords'][index]['price_currency']
            )

    def test_login_required(self):
        """
        Users are required to login before accessing the view.
        """
        self.client.logout()
        response = self.client.get(self.path)
        self.assertEqual(response.status_code, 401)

    def test_journal_product_view(self):
        """
        Tests 'GET' end point for JournalProductViewSet.
        """
        response = self.client.get(self.path)
        response_data = json.loads(response.content)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response_data['count'], 1)
        self.assertEqual(response_data['results'][0]['product_class'], "Journal")

    def test_update_with_invalid_data(self):
        """
        Tests 'PUT' end point for JournalProductViewSet with invalid data.
        """
        product_title = self.product.title
        path = reverse(
            'journal:api:v1:journal-detail',
            kwargs={'attribute_values__value_text': self.value_text}
        )
        self.client.put(
            path,
            json.dumps(
                {
                    "dummy-key1": "dummy-value1",
                    "dummy-key2": "dummy-value2"
                }
            ),
            "application/json"
        )

        # PUT endpoint always return 200 status code.
        self.assertEqual(self._get_product()['title'], product_title)

    def test_update_with_valid_data(self):
        """
        Tests 'PUT' end point for JournalProductViewSet with valid data.
        """
        path = reverse(
            'journal:api:v1:journal-detail',
            kwargs={'attribute_values__value_text': self.value_text}
        )
        response = self.client.put(path, json.dumps(self._get_data_for_put_endpoint()), "application/json")
        self.assertEqual(response.status_code, 200)
        self._assert_product_update()