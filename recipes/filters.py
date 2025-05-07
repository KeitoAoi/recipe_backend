# recipes/filters.py
import django_filters as df
from .models import Recipe

class RecipeFilter(df.FilterSet):
    total_mins_lt = df.NumberFilter(field_name="total_mins", lookup_expr="lt")
    total_mins_lte = df.NumberFilter(field_name="total_mins", lookup_expr="lte")
    recipe_category = df.CharFilter(field_name="category", lookup_expr="iexact")

    class Meta:
        model  = Recipe
        fields = []          # explicit filters above
