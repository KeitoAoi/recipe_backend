# recipes/management/commands/seed_demo_catalogs.py
import random
from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from ...models import Catalog, CatalogRecipe, Recipe

CATALOGS = ["Quick Meals", "Desserts", "Healthy Picks"]

class Command(BaseCommand):
    help = "Create three demo catalogs with three recipes each for every user"

    def handle(self, *args, **opts):
        all_recipes = list(Recipe.objects.all())
        if len(all_recipes) < 3:
            self.stderr.write("Need at least 3 recipes in DB.")
            return

        for user in get_user_model().objects.all():
            for name in CATALOGS:
                catalog, _ = Catalog.objects.get_or_create(user=user, name=name)
                # clear existing for idempotency
                CatalogRecipe.objects.filter(catalog=catalog).delete()

                picks = random.sample(all_recipes, 3)
                CatalogRecipe.objects.bulk_create(
                    [CatalogRecipe(catalog=catalog, recipe=r) for r in picks]
                )

        self.stdout.write(self.style.SUCCESS("Demo catalogs seeded."))
