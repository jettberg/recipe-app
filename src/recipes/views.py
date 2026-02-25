from django.shortcuts import render, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.utils.safestring import mark_safe

from .models import Recipe, Ingredient
from .forms import RecipeSearchForm

import pandas as pd
import matplotlib
matplotlib.use("Agg")  # required for server-side chart rendering
import matplotlib.pyplot as plt

import io
import base64


def _plot_to_base64() -> str:
    """Convert the current matplotlib figure into a base64 string."""
    buffer = io.BytesIO()
    plt.tight_layout()
    plt.savefig(buffer, format="png")
    plt.close()
    buffer.seek(0)
    img_base64 = base64.b64encode(buffer.getvalue()).decode("utf-8")
    return img_base64


def home(request):
    return render(request, "recipes/recipes_home.html")


@login_required
def recipe_list(request):
    recipes = Recipe.objects.all().order_by("-created_at")
    return render(request, "recipes/recipes_list.html", {"recipes": recipes})


@login_required
def recipe_detail(request, pk):
    recipe = get_object_or_404(Recipe, pk=pk)
    calculated_difficulty = recipe.calculate_difficulty()
    return render(
        request,
        "recipes/recipe_detail.html",
        {"recipe": recipe, "calculated_difficulty": calculated_difficulty},
    )


def logout_success(request):
    return render(request, "recipes/success.html")


@login_required
def recipe_search(request):
    """
    Search recipes by name and/or ingredient (partial matches allowed),
    optionally filter by difficulty, and show results in a pandas HTML table.
    Also generate bar/pie/line charts.
    """
    form = RecipeSearchForm(request.GET or None)

    # Default queryset
    qs = Recipe.objects.all().order_by("-created_at")

    # Apply filters only if form is valid
    if form.is_valid():
        query = (form.cleaned_data.get("query") or "").strip()
        difficulty = form.cleaned_data.get("difficulty") or ""
        show_all = form.cleaned_data.get("show_all") or False

        if not show_all:
            if query:
                # Partial matching using icontains
                qs = qs.filter(
                    name__icontains=query
                ) | qs.filter(
                    ingredients__name__icontains=query
                )
                qs = qs.distinct()

            if difficulty:
                qs = qs.filter(difficulty=difficulty)

    # ----------------------------
    # Build pandas DataFrame table
    # ----------------------------
    rows = []
    for r in qs:
        detail_url = f"/recipes/{r.pk}/"
        clickable_name = f'<a href="{detail_url}">{r.name}</a>'
        rows.append(
            {
                "Recipe": clickable_name,
                "Cooking Time (min)": r.cooking_time,
                "Difficulty": r.difficulty,
                "Created At": r.created_at.strftime("%Y-%m-%d %H:%M"),
            }
        )

    df = pd.DataFrame(rows)
    if not df.empty:
        table_html = df.to_html(index=False, escape=False)
        table_html = mark_safe(table_html)
    else:
        table_html = None

    # ----------------------------
    # Charts (use ALL recipes for analysis, not only filtered)
    # ----------------------------
    all_recipes = Recipe.objects.all()

    # Bar chart: top ingredients
    ingredient_counts = (
        Ingredient.objects
        .filter(recipes__in=all_recipes)
        .distinct()
        .values("name")
    )

    # Count recipes per ingredient (simple + clear)
    ing_labels = []
    ing_values = []
    for ing in Ingredient.objects.all().order_by("name"):
        count = ing.recipes.count()
        if count > 0:
            ing_labels.append(ing.name)
            ing_values.append(count)

    bar_chart = None
    if ing_values:
        # Take top 8 to avoid messy chart
        top = sorted(zip(ing_labels, ing_values), key=lambda x: x[1], reverse=True)[:8]
        labels = [x[0] for x in top]
        values = [x[1] for x in top]

        plt.figure()
        plt.bar(labels, values)
        plt.title("Top Ingredients (by recipe count)")
        plt.xlabel("Ingredient")
        plt.ylabel("Recipes")
        plt.xticks(rotation=30, ha="right")
        bar_chart = _plot_to_base64()

    # Pie chart: difficulty distribution
    diff_counts = {"Easy": 0, "Medium": 0, "Intermediate": 0, "Hard": 0}
    for r in all_recipes:
        if r.difficulty in diff_counts:
            diff_counts[r.difficulty] += 1

    pie_chart = None
    if sum(diff_counts.values()) > 0:
        labels = [k for k, v in diff_counts.items() if v > 0]
        sizes = [v for v in diff_counts.values() if v > 0]

        plt.figure()
        plt.pie(sizes, labels=labels, autopct="%1.0f%%")
        plt.title("Difficulty Distribution")
        pie_chart = _plot_to_base64()

    # Line chart: recipes created per day
    dates = []
    for r in all_recipes:
        dates.append(r.created_at.date())

    line_chart = None
    if dates:
        date_series = pd.Series(dates)
        grouped = date_series.value_counts().sort_index()  # index=date, value=count

        plt.figure()
        plt.plot(grouped.index.astype(str), grouped.values, marker="o")
        plt.title("Recipes Created Over Time")
        plt.xlabel("Date")
        plt.ylabel("Recipes created")
        plt.xticks(rotation=30, ha="right")
        line_chart = _plot_to_base64()

    context = {
        "form": form,
        "table_html": table_html,
        "bar_chart": bar_chart,
        "pie_chart": pie_chart,
        "line_chart": line_chart,
    }
    return render(request, "recipes/recipe_search.html", context)