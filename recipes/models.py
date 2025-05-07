from django.db import models
from django.contrib.auth.models import User
from django.contrib.postgres.fields import ArrayField
from django.contrib.postgres.search import SearchVectorField
from django.contrib.postgres.indexes import GinIndex


class Profile(models.Model):
    """
    Extends the default User model with additional profile information.
    """
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    name = models.CharField(max_length=255, blank=True)
    profile_pic = models.ImageField(upload_to='profile_pics/', null=True, blank=True)

    def __str__(self):
        return self.user.username


class RecipeCategory(models.Model):
    """
    High-level grouping for recipes (e.g., "Dessert", "Main Course").
    """
    name = models.CharField(max_length=100, unique=True)

    def __str__(self):
        return self.name


class Ingredient(models.Model):
    """
    Individual ingredient names, used in RecipeIngredient.
    """
    name = models.CharField(max_length=200, unique=True)

    def __str__(self):
        return self.name


class Recipe(models.Model):
    """
    Core recipe data, mapped from the CSV columns.
    """
    recipe_id = models.IntegerField(unique=True)
    name = models.CharField(max_length=500)
    cook_mins = models.FloatField(null=True, blank=True)
    prep_mins = models.FloatField(null=True, blank=True)
    total_mins = models.FloatField(null=True, blank=True)
    category = models.ForeignKey(
        RecipeCategory,
        on_delete=models.SET_NULL,
        null=True,
        related_name='recipes'
    )
    calories = models.FloatField(null=True, blank=True)
    fat_content = models.FloatField(null=True, blank=True)
    saturated_fat_content = models.FloatField(null=True, blank=True)
    cholesterol_content = models.FloatField(null=True, blank=True)
    sodium_content = models.FloatField(null=True, blank=True)
    carbohydrate_content = models.FloatField(null=True, blank=True)
    fiber_content = models.FloatField(null=True, blank=True)
    sugar_content = models.FloatField(null=True, blank=True)
    protein_content = models.FloatField(null=True, blank=True)
    keywords = ArrayField(
        base_field=models.CharField(max_length=100),
        default=list,
        blank=True
    )
    images = ArrayField(
        base_field=models.URLField(),
        default=list,
        blank=True
    )
    instructions = models.TextField(blank=True)
    ingredients = models.ManyToManyField(
        Ingredient,
        through='RecipeIngredient',
        related_name='recipes'
    )
    # Full-text search vector field
    search_vector = SearchVectorField(null=True, editable=False)

    class Meta:
        indexes = [
            GinIndex(fields=['search_vector']),
        ]

    def __str__(self):
        return f"{self.name} (ID: {self.recipe_id})"


class RecipeIngredient(models.Model):
    """
    Through model linking Recipes and Ingredients with quantity info.
    """
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        related_name='recipe_ingredients'
    )
    ingredient = models.ForeignKey(
        Ingredient,
        on_delete=models.CASCADE
    )
    quantity = models.CharField(max_length=100)

    def __str__(self):
        return f"{self.quantity} of {self.ingredient.name} in {self.recipe.name}"


class Catalog(models.Model):
    """
    User-created grouping of recipes (like a Spotify playlist).
    """
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='catalogs'
    )
    name = models.CharField(max_length=255)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('user', 'name')

    def __str__(self):
        return f"{self.name} ({self.user.username})"


class CatalogRecipe(models.Model):
    """
    Links recipes to a user catalog.
    """
    catalog = models.ForeignKey(
        Catalog,
        on_delete=models.CASCADE,
        related_name='catalog_recipes'
    )
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE
    )
    added_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('catalog', 'recipe')

    def __str__(self):
        return f"{self.recipe.name} in {self.catalog.name}"


class Favorite(models.Model):
    """
    Tracks user-favorited recipes.
    """
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='favorites'
    )
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE
    )
    favorited_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('user', 'recipe')

    def __str__(self):
        return f"{self.user.username} favorited {self.recipe.name}"


# recipes/models.py
class RecipeAccess(models.Model):
    user        = models.ForeignKey(User, on_delete=models.CASCADE)
    recipe      = models.ForeignKey(Recipe, on_delete=models.CASCADE)
    accessed_at = models.DateTimeField(auto_now=True)   # ← auto-update every hit

    class Meta:
        unique_together = ("user", "recipe")            # 1 row per recipe+user
        ordering = ("-accessed_at",)                    # newest first
    def __str__(self):
        return f"{self.user.username} accessed {self.recipe.name} at {self.accessed_at}"


class Allergen(models.Model):
    """
    Predefined list of possible allergens (e.g., "Peanuts").
    """
    name = models.CharField(max_length=100, unique=True)

    def __str__(self):
        return self.name


class UserAllergy(models.Model):
    """
    Links users to allergens they wish to avoid.
    """
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='allergies'
    )
    allergen = models.ForeignKey(
        Allergen,
        on_delete=models.CASCADE
    )

    class Meta:
        unique_together = ('user', 'allergen')

    def __str__(self):
        return f"{self.user.username} allergic to {self.allergen.name}"


# Models for predefined catalogs in Browse section
class PredefinedCatalogType(models.Model):
    """
    Groups predefined catalogs under a common type (e.g., "Meal Type").
    """
    name = models.CharField(max_length=255, unique=True)

    def __str__(self):
        return self.name


class PredefinedCatalog(models.Model):
    """
    Predefined catalogs (e.g., "Breakfast", "< 15 Mins") with filter criteria.
    """
    type = models.ForeignKey(
        PredefinedCatalogType,
        on_delete=models.CASCADE,
        related_name='catalogs'
    )
    name = models.CharField(max_length=255)
    filter_criteria = models.JSONField(
        default=dict,
        help_text='Django ORM filter kwargs for this catalog'
    )

    class Meta:
        unique_together = ('type', 'name')

    def __str__(self):
        return f"{self.name} ({self.type.name})"
