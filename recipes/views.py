# recipes/views.py
from rest_framework import generics, viewsets, permissions, status
from rest_framework.decorators import action
from rest_framework.response import Response
from .serializers import SignupSerializer
from django.contrib.auth.models import User
from django.contrib.postgres.search import SearchVector, SearchQuery, SearchRank
from rest_framework.views import APIView
from .serializers import SlimRecipeSerializer
from django.db.models import Case, When, IntegerField

from .models import (
    Recipe,
    Favorite,
    Catalog,
    CatalogRecipe,
    RecipeAccess,
    PredefinedCatalogType,
    PredefinedCatalog,
)
from .serializers import (
    SlimRecipeSerializer,
    RecipeSerializer,
    CatalogSerializer,
    PredefinedCatalogTypeSerializer,
    PredefinedCatalogSerializer,
)

# ───────────────────────────────────────────────────────────────
# Helper: default permission
AUTH = [permissions.IsAuthenticated]


# ───────────────────────────────────────────────────────────────
# 1 ·  Favourite list  (first 3 for the current user)
class FavoriteList(generics.ListAPIView):
    serializer_class = SlimRecipeSerializer
    permission_classes = AUTH

    def get_queryset(self):
        return (
            Recipe.objects.filter(favorite__user=self.request.user)[:3]
        )  # favourite is FK reverse name


# ───────────────────────────────────────────────────────────────
# 2 ·  Recently accessed list (last 3)
class RecentList(generics.ListAPIView):
    serializer_class = SlimRecipeSerializer
    permission_classes = AUTH

    def get_queryset(self):
        ids = (
            RecipeAccess.objects.filter(user=self.request.user)
            .order_by("-accessed_at")
            .values_list("recipe_id", flat=True)[:3]
        )
        return Recipe.objects.filter(id__in=ids)


# ───────────────────────────────────────────────────────────────
# Catalog CRUD (create/list/retrieve) + add & remove recipe
class CatalogViewSet(viewsets.ModelViewSet):
    """
    • GET  /api/catalogs/               – list user catalogs
    • POST /api/catalogs/               – create new catalog   (name)
    • GET  /api/catalogs/<pk>/          – retrieve one catalog
    • POST /api/catalogs/<pk>/add-recipe/          – add recipe
    • DELETE /api/catalogs/<pk>/remove-recipe/<rid>/ – remove recipe
    """
    serializer_class   = CatalogSerializer
    permission_classes = AUTH
    http_method_names  = ["get", "post", "delete"]      # no update/partial_update

    # ---- queryset limited to this user ----
    def get_queryset(self):
        return (
            Catalog.objects
            .filter(user=self.request.user)
            .prefetch_related("catalog_recipes__recipe")
        )

    # ---- create new catalog ----
    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

    # ---- POST /api/catalogs/<pk>/add-recipe/ ----
    @action(detail=True, methods=["post"], url_path="add-recipe")
    def add_recipe(self, request, pk=None):
        recipe_id = request.data.get("recipe_id")
        if not recipe_id:
            return Response({"detail": "recipe_id required"}, status=400)

        catalog = self.get_object()
        try:
            recipe = Recipe.objects.get(recipe_id=recipe_id)
        except Recipe.DoesNotExist:
            return Response({"detail": "Recipe not found"}, status=404)

        CatalogRecipe.objects.get_or_create(catalog=catalog, recipe=recipe)
        return Response({"detail": "Recipe added"}, status=status.HTTP_201_CREATED)

    # ---- DELETE /api/catalogs/<pk>/remove-recipe/<rid>/ ----
    @action(
        detail=True,
        methods=["delete"],
        url_path=r"remove-recipe/(?P<recipe_id>\d+)"
    )
    def remove_recipe(self, request, pk=None, recipe_id=None):
        catalog = self.get_object()
        deleted, _ = CatalogRecipe.objects.filter(
            catalog=catalog,
            recipe__recipe_id=recipe_id
        ).delete()

        if deleted:
            return Response(status=status.HTTP_204_NO_CONTENT)
        return Response(
            {"detail": "Recipe not found in this catalog"},
            status=status.HTTP_404_NOT_FOUND
        )


# ───────────────────────────────────────────────────────────────
# 4 ·  Recipe list / detail  (lookup by recipe_id)
# recipes/views.py
from django.utils import timezone
from django.db.models import F
from .filters import RecipeFilter
class RecipeViewSet(viewsets.ReadOnlyModelViewSet):
    lookup_field = "recipe_id"
    queryset = Recipe.objects.all()
    serializer_class = RecipeSerializer
    permission_classes = [permissions.AllowAny]
    filterset_class = RecipeFilter

    # def get_serializer_context(self):
    #     ctx = super().get_serializer_context()
    #     ctx["request"] = self.request          # <- make request available
    #     return ctx

    def retrieve(self, request, *args, **kwargs):
        response = super().retrieve(request, *args, **kwargs)

        if request.user.is_authenticated:
            recipe = self.get_object()

            # 1️⃣  upsert with fresh timestamp
            RecipeAccess.objects.update_or_create(
                user=request.user, recipe=recipe,
                defaults={"accessed_at": timezone.now()}
            )

            # 2️⃣  keep only 10 newest for this user
            recent_ids = (
                RecipeAccess.objects
                .filter(user=request.user)
                .order_by("-accessed_at")
                .values_list("id", flat=True)[:10]
            )
            RecipeAccess.objects.filter(user=request.user).exclude(id__in=recent_ids).delete()

        return response



# ───────────────────────────────────────────────────────────────
# 5 ·  Predefined catalog browsing
class PredefinedCatalogTypeViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = PredefinedCatalogType.objects.all()
    serializer_class = PredefinedCatalogTypeSerializer
    permission_classes = [permissions.AllowAny]


class PredefinedCatalogViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = PredefinedCatalog.objects.all()
    serializer_class = PredefinedCatalogSerializer
    permission_classes = [permissions.AllowAny]

class SignupView(generics.CreateAPIView):
    """
    POST /api/auth/signup/
    Body: { "username": "alice", "email": "a@x.com", "password": "secret" }

    Returns:
    {
      "username": "alice",
      "email": "a@x.com",
      "token": { "access": "...", "refresh": "..." }
    }
    """
    queryset = User.objects.all()
    serializer_class = SignupSerializer
    permission_classes = [permissions.AllowAny]

from rest_framework import generics, viewsets, mixins, permissions, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django.shortcuts import get_object_or_404

from .models import Recipe, Favorite, Catalog, CatalogRecipe, RecipeAccess
from .serializers import (
    SlimRecipeSerializer, RecipeSerializer, CatalogSerializer,
    CatalogCreateSerializer, FavoriteCreateSerializer
)

# AUTH = [permissions.IsAuthenticated]

# ───── 1. Favourite toggle ───────────────────────────────────────
class FavoriteViewSet(viewsets.ModelViewSet):          # 🟢 ModelViewSet → allows POST
    permission_classes = [permissions.IsAuthenticated]
    lookup_field = "recipe_id"                         # URL uses /favorites/<recipe_id>/
    http_method_names = ["get", "post", "delete"]      # (optional limit)

    # List should return slim recipe objects (image + name)
    serializer_class = SlimRecipeSerializer

    def get_queryset(self):
        return Recipe.objects.filter(
            favorite__user=self.request.user
        ).distinct()

    # ---------- Create ----------
    def create(self, request, *args, **kwargs):
        # expect body: { "recipe_id": 462697 }
        serializer = FavoriteCreateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        rid = serializer.validated_data["recipe_id"]

        recipe = get_object_or_404(Recipe, recipe_id=rid)
        Favorite.objects.get_or_create(user=request.user, recipe=recipe)
        return Response({"detail": "added"}, status=status.HTTP_201_CREATED)

    # ---------- Destroy ----------
    def destroy(self, request, *args, **kwargs):
        rid = kwargs.get("recipe_id")
        Favorite.objects.filter(
            user=request.user, recipe__recipe_id=rid
        ).delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
class CatalogViewSet(viewsets.ModelViewSet):
    serializer_class   = CatalogSerializer
    permission_classes = [permissions.IsAuthenticated]
    lookup_field       = "id"

    def get_queryset(self):
        # only the user's own catalogs
        return (Catalog.objects
                .filter(user=self.request.user)
                .prefetch_related("catalog_recipes__recipe"))

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

    @action(detail=True, methods=["post"], url_path="add-recipe")
    def add_recipe(self, request, id=None):
        rid = request.data.get("recipe_id")
        if not rid:
            return Response({"detail": "recipe_id required"}, status=400)
        recipe = get_object_or_404(Recipe, recipe_id=rid)
        CatalogRecipe.objects.get_or_create(catalog=self.get_object(), recipe=recipe)
        return Response({"detail": "added"}, status=status.HTTP_201_CREATED)

    # NEW: allow client to delete one recipe from the catalog
    @action(detail=True, methods=["delete"], url_path=r"remove-recipe/(?P<recipe_id>\d+)")
    def remove_recipe(self, request, id=None, recipe_id=None):
        CatalogRecipe.objects.filter(
            catalog=self.get_object(),
            recipe__recipe_id=recipe_id
        ).delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class RecentList(generics.ListAPIView):
    serializer_class    = SlimRecipeSerializer
    permission_classes  = [permissions.IsAuthenticated]

    def get_queryset(self):
        ids = list(                # turn the queryset into a Python list
            RecipeAccess.objects
            .filter(user=self.request.user)
            .order_by("-accessed_at")
            .values_list("recipe__recipe_id", flat=True)[:10]
        )

        if not ids:
            return Recipe.objects.none()

        # build CASE … WHEN … THEN … END
        ordering = Case(
            *[When(recipe_id=rid, then=pos) for pos, rid in enumerate(ids)],
            output_field=IntegerField(),
        )

        return (
            Recipe.objects
            .filter(recipe_id__in=ids)
            .order_by(ordering)     # ⬅ preserved newest‑first
        )


# ───── search feature ────────────────────
class SearchView(APIView):
    permission_classes = [permissions.AllowAny]

    def get(self, request):
        query      = request.query_params.get("q", "")
        exclude_id = request.query_params.get("exclude")   # ← NEW
        limit      = int(request.query_params.get("limit", 10))

        if not query:
            return Response({"results": []})

        vector = (
            SearchVector("name", weight="A") +
            SearchVector("keywords", weight="B") +
            SearchVector("ingredients__name", weight="B")
        )
        qs = (
            Recipe.objects
            .annotate(rank=SearchRank(vector, SearchQuery(query)))
            .filter(rank__gte=0.1)
            .order_by("-rank")
            .distinct()
        )

        if exclude_id:
            qs = qs.exclude(recipe_id=exclude_id)

        serializer = SlimRecipeSerializer(qs[:limit], many=True)
        return Response({"results": serializer.data})
