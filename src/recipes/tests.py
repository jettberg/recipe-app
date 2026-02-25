from django.test import TestCase
from django.urls import reverse
from django.contrib.auth.models import User
from .models import Recipe, Ingredient


class RecipeViewsTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username="testuser", password="testpass123")
        self.salt = Ingredient.objects.create(name="Salt")

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
        self.assertContains(response, "Welcome")

    def test_recipe_list_loads(self):
        url = reverse("recipes:recipe_list")
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Recipes")
        self.assertContains(response, "Test Soup")

    def test_recipe_detail_loads(self):
        url = reverse("recipes:recipe_detail", args=[self.recipe.pk])
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Test Soup")
        self.assertContains(response, "Cooking time")