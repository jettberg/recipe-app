from django.db import models
from django.contrib.auth.models import User


class Ingredient(models.Model):
    name = models.CharField(max_length=100, unique=True)

    def __str__(self):
        return self.name


class Recipe(models.Model):
    name = models.CharField(max_length=200)

    # Keep ImageField if you want, but it won't work on Heroku without cloud storage
    image = models.ImageField(upload_to="recipe_images/", blank=True, null=True)

    # NEW: filename for images stored in /static/recipes/images/
    static_image = models.CharField(
        max_length=200,
        blank=True,
        help_text="Example: tomato_soup.jpg (stored in static/recipes/images/)"
    )

    description = models.TextField(blank=True)
    cooking_time = models.PositiveIntegerField()
    difficulty = models.CharField(max_length=20, blank=True)
    ingredients = models.ManyToManyField(Ingredient, related_name="recipes")
    created_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name="recipes")
    created_at = models.DateTimeField(auto_now_add=True)

    def calculate_difficulty(self) -> str:
        ing_count = self.ingredients.count()

        if self.cooking_time < 10 and ing_count < 4:
            return "Easy"
        elif self.cooking_time < 10 and ing_count >= 4:
            return "Medium"
        elif self.cooking_time >= 10 and ing_count < 4:
            return "Intermediate"
        else:
            return "Hard"

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        new_diff = self.calculate_difficulty()
        if self.difficulty != new_diff:
            self.difficulty = new_diff
            super().save(update_fields=["difficulty"])

    def __str__(self):
        return self.name