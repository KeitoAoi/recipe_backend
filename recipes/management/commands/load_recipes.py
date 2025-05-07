import csv
import json
from django.core.management.base import BaseCommand
from recipes.models import (
    Recipe, RecipeCategory, Ingredient, RecipeIngredient,
    Catalog, CatalogRecipe
)

class Command(BaseCommand):
    help = "Load recipes from a CSV file"

    def add_arguments(self, parser):
        parser.add_argument(
            "--path",
            type=str,
            required=True,
            help="Path to the CSV file"
        )

    def handle(self, *args, **options):
        path = options["path"]
        with open(path, newline='', encoding='utf-8') as csvfile:
            reader = csv.DictReader(csvfile)
            self.stdout.write(f"Loading recipes from {path}...")
            for row in reader:
                # 1) Category
                cat_name = row["RecipeCategory"]
                category, _ = RecipeCategory.objects.get_or_create(name=cat_name)

                # 2) Recipe core
                r, created = Recipe.objects.get_or_create(
                    recipe_id=int(row["RecipeId"]),
                    defaults={
                        "name": row["Name"],
                        "cook_mins": row["CookMins"] or None,
                        "prep_mins": row["PrepMins"] or None,
                        "total_mins": row["TotalMins"] or None,
                        "category": category,
                        "calories": float(row["Calories"]),
                        # … repeat for other nutrition fields …
                        "keywords": json.loads(row["Keywords"]),
                        "images": json.loads(row["Images"]),
                        "instructions": row["RecipeInstructions"],
                    }
                )
                if not created:
                    continue

                # 3) Ingredients
                ingredients = json.loads(row["IngredientList"])
                quantities  = json.loads(row["Quantities"])
                for name, qty in zip(ingredients, quantities):
                    ing, _ = Ingredient.objects.get_or_create(name=name)
                    RecipeIngredient.objects.create(
                        recipe=r,
                        ingredient=ing,
                        quantity=qty
                    )

            self.stdout.write(self.style.SUCCESS("Import complete!"))
