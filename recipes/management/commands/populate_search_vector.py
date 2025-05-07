from django.core.management.base import BaseCommand
from django.contrib.postgres.search import SearchVector
from django.db import models
from ...models import Catalog, CatalogRecipe, Recipe

class Command(BaseCommand):
    help = "Populate the search_vector field for all recipes"

    def handle(self, *args, **kwargs):
        recipes = Recipe.objects.prefetch_related('ingredients').all()
        count = 0

        for recipe in recipes:
            ingredient_names = " ".join([ing.name for ing in recipe.ingredients.all()])
            recipe.search_vector = (
                SearchVector('name', weight='A') +
                SearchVector('keywords', weight='B') +
                SearchVector(models.Value(ingredient_names), config='english')
            )
            recipe.save(update_fields=['search_vector'])
            count += 1

        self.stdout.write(self.style.SUCCESS(f"Updated search_vector for {count} recipes."))
