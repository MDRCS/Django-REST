from django.contrib.auth import get_user_model
from django.urls import reverse
from django.test import TestCase

from rest_framework import status
from rest_framework.test import APIClient

from core.models import Tag, Recipe

from recipe.serializers import TagSerializer

TAGS_URL = reverse('recipe:tag-list')


class PublicTagsAPITest(TestCase):
    """ Test publicly available  """

    def setUp(self):
        self.client = APIClient()

    def test_login_required(self):
        """ list tags """
        res = self.client.get(TAGS_URL)
        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)


class PrivateTagsAPITest(TestCase):

    def setUp(self):
        self.user = get_user_model().objects.create_user(
            'test@rahali.com',
            'pass123'
        )
        self.client = APIClient()
        self.client.force_authenticate(user=self.user)

    def test_retrieve_tags(self):
        Tag.objects.create(user=self.user, name='Vegan')
        Tag.objects.create(user=self.user, name='Dessert')

        res = self.client.get(TAGS_URL)
        tags = Tag.objects.all().order_by('-name')
        serializer = TagSerializer(tags, many=True)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, serializer.data)

    def test_tags_limited_user(self):
        """ Test that tags retrieve are limited to user """
        Tag.objects.create(user=self.user, name='Vegan')
        user_2 = get_user_model().objects.create_user(
            'user_2@rahali.com',
            'pass123'
        )
        Tag.objects.create(user=user_2, name='Dessert')

        res = self.client.get(TAGS_URL)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data[0]['name'], 'Vegan')
        self.assertNotIn('Dessert', res.data)

    def test_tags_created_successful(self):
        """ Test creating a new tag """
        payload = {'name': 'Test tag'}
        self.client.post(TAGS_URL, payload)

        exists = Tag.objects.filter(
            user=self.user,
            name=payload['name']
        ).exists()

        self.assertTrue(exists)

    def test_create_tag_invalid(self):
        """ Test creating a new tag with invalid name """
        payload = {'name': ''}
        res = self.client.post(TAGS_URL, payload)

        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

    def test_retrieve_tags_assigned_recipes(self):
        tag_1 = Tag.objects.create(user=self.user, name='Breakfast')
        tag_2 = Tag.objects.create(user=self.user, name='Dinner')
        recipe = Recipe.objects.create(
            title='Coriander eggs on toast',
            time_minutes=25,
            price=5.00,
            user=self.user
        )

        recipe.tags.add(tag_1)
        res = self.client.get(TAGS_URL, {'assigned_only': 1})
        serializer_1 = TagSerializer(tag_1)
        serializer_2 = TagSerializer(tag_2)
        self.assertIn(serializer_1.data, res.data)
        self.assertNotIn(serializer_2.data, res.data)
