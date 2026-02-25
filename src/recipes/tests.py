from django.test import TestCase
from django.urls import reverse
from django.contrib.auth.models import User

from .models import Recipe, Ingredient


class RecipeAuthAndViewsTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username="testuser", password="testpass123")

        self.salt = Ingredient.objects.create(name="Salt")
        self.sugar = Ingredient.objects.create(name="Sugar")

        self.recipe = Recipe.objects.create(
            name="Test Soup",
            description="A simple test soup",
            cooking_time=5,
            created_by=self.user,
        )
        self.recipe.ingredients.add(self.salt)

    def test_home_page_loads(self):
        url = reverse("recipes:home")
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)

    def test_recipes_list_requires_login(self):
        url = reverse("recipes:recipe_list")
        response = self.client.get(url)
        self.assertEqual(response.status_code, 302)  # redirect to login

    def test_recipes_detail_requires_login(self):
        url = reverse("recipes:recipe_detail", args=[self.recipe.pk])
        response = self.client.get(url)
        self.assertEqual(response.status_code, 302)

    def test_search_requires_login(self):
        url = reverse("recipes:recipe_search")
        response = self.client.get(url)
        self.assertEqual(response.status_code, 302)

    def test_search_returns_results_after_login(self):
        self.client.login(username="testuser", password="testpass123")

        url = reverse("recipes:recipe_search")
        response = self.client.get(url, {"query": "Soup"})
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Test Soup")

    def test_partial_search_works(self):
        self.client.login(username="testuser", password="testpass123")

        url = reverse("recipes:recipe_search")
        response = self.client.get(url, {"query": "Sou"})
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Test Soup")