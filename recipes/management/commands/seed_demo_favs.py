
from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from ...models import Recipe, Favorite

class Command(BaseCommand):
    help = "Seed three favourite recipes for every user (demo only)"

    def handle(self, *args, **opts):
        first_three = list(Recipe.objects.all()[:3])
        for user in get_user_model().objects.all():
            for r in first_three:
                Favorite.objects.get_or_create(user=user, recipe=r)
        self.stdout.write(self.style.SUCCESS("Demo favourites created."))
