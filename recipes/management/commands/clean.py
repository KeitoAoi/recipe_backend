from .models import PredefinedCatalog

patched = 0
for pc in PredefinedCatalog.objects.all():
    crit = pc.filter_criteria or {}

    # fix Cook-Time keys that were stored with a double-underscore
    if "total_mins__lt" in crit:
        crit["total_mins_lt"] = crit.pop("total_mins__lt")
        pc.filter_criteria = crit
        pc.save(update_fields=["filter_criteria"])
        patched += 1

print(f"✅  Patched {patched} predefined catalogs.")
