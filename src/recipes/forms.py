from django import forms
from .models import Recipe, Ingredient


class RecipeSearchForm(forms.Form):
    query = forms.CharField(
        required=False,
        max_length=100,
        label="Search",
        widget=forms.TextInput(attrs={"placeholder": "Search by recipe name or ingredient..."}),
    )

    difficulty = forms.ChoiceField(
        required=False,
        choices=[
            ("", "Any difficulty"),
            ("Easy", "Easy"),
            ("Medium", "Medium"),
            ("Intermediate", "Intermediate"),
            ("Hard", "Hard"),
        ],
        label="Difficulty",
    )

    show_all = forms.BooleanField(required=False, label="Show all recipes")


class RecipeForm(forms.ModelForm):
    ingredients_text = forms.CharField(
        label="Ingredients (comma-separated)",
        required=True,
        widget=forms.TextInput(attrs={"placeholder": "eggs, milk, sugar"}),
        help_text="Example: eggs, milk, sugar",
    )

    class Meta:
        model = Recipe
        fields = ["name", "description", "cooking_time", "image"]

    def save(self, commit=True, created_by=None):
        recipe = super().save(commit=False)

        if created_by is not None:
            recipe.created_by = created_by

        if commit:
            recipe.save()

            raw = self.cleaned_data.get("ingredients_text", "")
            ing_names = [i.strip() for i in raw.split(",") if i.strip()]

            ingredient_objs = []
            for name in ing_names:
                obj, _ = Ingredient.objects.get_or_create(name=name)
                ingredient_objs.append(obj)

            recipe.ingredients.set(ingredient_objs)

            # recompute difficulty using your model logic
            recipe.save()

        return recipe