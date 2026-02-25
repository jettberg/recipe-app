from django.shortcuts import render, get_object_or_404
from .models import Recipe


def home(request):
    return render(request, "recipes/recipes_home.html")


def recipe_list(request):
    recipes = Recipe.objects.all().order_by("-created_at")
    return render(request, "recipes/recipes_list.html", {"recipes": recipes})


def recipe_detail(request, pk):
    recipe = get_object_or_404(Recipe, pk=pk)
    # difficulty is already stored, but we can also display calculated difficulty for safety
    calculated_difficulty = recipe.calculate_difficulty()
    return render(
        request,
        "recipes/recipe_detail.html",
        {"recipe": recipe, "calculated_difficulty": calculated_difficulty},
    )