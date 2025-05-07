from django.core.management.base import BaseCommand
from ...models import PredefinedCatalogType, PredefinedCatalog


class Command(BaseCommand):
    help = "Seed predefined catalog types and catalogs for browse section"

    def handle(self, *args, **options):
        predefined = {
            "Meal Type": ["Breakfast", "Dessert", "Lunch/Snacks", "Beverages"],
            "Cook Time": ["< 15 Mins", "< 30 Mins", "< 60 Mins"]
        }

        for type_name, catalog_names in predefined.items():
            ctype, _ = PredefinedCatalogType.objects.get_or_create(name=type_name)
            self.stdout.write(f"Ensured catalog type: {type_name}")

            for cat_name in catalog_names:
                # Determine filter criteria for Cook Time catalogs
                if type_name == "Cook Time":
                    if cat_name == "< 15 Mins":
                        criteria = {"total_mins_lt": 15}
                    elif cat_name == "< 30 Mins":
                        criteria = {"total_mins_lt": 30}
                    elif cat_name == "< 60 Mins":
                        criteria = {"total_mins_lt": 60}
                    else:
                        criteria = {}
                else:
                    criteria = {}

                PredefinedCatalog.objects.get_or_create(
                    type=ctype,
                    name=cat_name,
                    defaults={"filter_criteria": criteria}
                )
                self.stdout.write(f"  - Ensured catalog: {cat_name}")

        self.stdout.write(self.style.SUCCESS("Predefined catalogs seeded successfully."))
