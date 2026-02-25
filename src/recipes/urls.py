from django.urls import path
from . import views

app_name = "recipes"

urlpatterns = [
    path("", views.home, name="home"),
    path("about/", views.about, name="about"),
    path("recipes/", views.recipe_list, name="recipe_list"),
    path("recipes/add/", views.add_recipe, name="add_recipe"),
    path("recipes/<int:pk>/", views.recipe_detail, name="recipe_detail"),
    path("search/", views.recipe_search, name="recipe_search"),
]