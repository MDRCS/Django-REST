from django.contrib.auth import get_user_model
from django.urls import reverse
from django.test import TestCase

from rest_framework import status
from rest_framework.test import APIClient
from core.models import Ingredient
from recipe.serializers import IngredientSerializer

INGREDIENTS_URL = reverse('recipe:ingredient-list')


class PublicIngredientAPITest(TestCase):

    def setUp(self):
        self.client = APIClient()

    def test_login_required(self):
        """ Test that login is required to list Ingredients """
        res = self.client.get(INGREDIENTS_URL)

        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)


class PrivateIngredientAPITest(TestCase):

    def setUp(self):
        self.user = get_user_model().objects.create_user(
            'test@rahali.com',
            'pass123'
        )
        self.client = APIClient()
        self.client.force_authenticate(user=self.user)

    def test_retrieve_ingredients_list(self):
        Ingredient.objects.create(
            user=self.user,
            name='Kale'
        )
        Ingredient.objects.create(
            user=self.user,
            name='Salt'
        )

        res = self.client.get(INGREDIENTS_URL)
        ingredients = Ingredient.objects.all().order_by('-name')
        serializer = IngredientSerializer(ingredients, many=True)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, serializer.data)

    def test_ingredients_limited_to_authuser(self):
        user_2 = get_user_model().objects.create_user(
            'user_2@rahali.com',
            'pass123'
        )
        Ingredient.objects.create(
            user=user_2,
            name='Kale'
        )
        ingredient = Ingredient.objects.create(
            user=self.user,
            name='Salt'
        )

        res = self.client.get(INGREDIENTS_URL)
        self.assertEqual(res.data[0]['name'], ingredient.name)
        self.assertEqual(res.status_code, status.HTTP_200_OK)

    def test_create_ingredient_successful(self):
        """ Testing the creation of an ingredient """
        payload = {'name': 'Kale'}
        self.client.post(INGREDIENTS_URL, payload)

        exists = Ingredient.objects.filter(
            user=self.user,
            name=payload['name']
        ).exists()

        self.assertTrue(exists)

    def test_create_ingredient_invalid(self):
        """ Testing the creation of an invalid ingredient """
        payload = {'name': ''}
        res = self.client.post(INGREDIENTS_URL, payload)
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)
