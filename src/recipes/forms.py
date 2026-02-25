from django import forms


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