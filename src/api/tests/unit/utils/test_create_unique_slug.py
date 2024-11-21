import unittest
from django.test import TestCase
from django.utils.text import slugify
from datetime import datetime
from api.tests.common import makeUser
from database.models import CustomPage
from api.utils.api_utils import create_unique_slug


class CreateUniqueSlugTestCase(TestCase):
    def setUp(self):
        self.user = makeUser()
        CustomPage.objects.create(title="Testing", slug=slugify("testing"), user=self.user)
        CustomPage.objects.create(title="Wayland Testing", slug=slugify("wayland-testing"), user=self.user)
        CustomPage.objects.create(title="Another One", slug=slugify("another-one"), user=self.user)


    def test_create_unique_slug_no_title(self):
        result = create_unique_slug(None, CustomPage)
        self.assertIsNone(result)

    def test_create_unique_slug_no_model_or_field(self):
        title = "Test Title"
        result = create_unique_slug(title, None)
        self.assertEqual(result, slugify(title))

    def test_create_unique_slug_unique_slug(self):
        title = "Test Title"
        result = create_unique_slug(title, CustomPage)
        self.assertEqual(result, slugify(title))

    def test_create_unique_slug_with_prefix(self):
        title = "Testing for a new thing"

        result = create_unique_slug(title, CustomPage,"slug")
        self.assertEqual(result, f"{slugify(title)}".lower())

    def test_create_unique_slug_with_prefix_existing(self):
        title = "Testing"
        prefix = "Wayland"

        result = create_unique_slug(title, CustomPage,"slug")

        self.assertTrue(result.startswith(f"{slugify(title)}-".lower()))

    def test_create_unique_slug_with_timestamp(self):
        title = "Test Title"

        CustomPage.objects.create(title=title, slug=slugify(title), user=self.user)

        result = create_unique_slug(title, CustomPage)
        self.assertNotEqual(result, slugify(title))
        self.assertTrue(result.startswith(f"{slugify(title)}-".lower()))

if __name__ == "__main__":
    unittest.main()