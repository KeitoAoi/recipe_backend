from django.urls import path
from rest_framework.routers import DefaultRouter
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
    TokenBlacklistView,
)
from .views import RecipeViewSet, CatalogViewSet, PredefinedCatalogTypeViewSet, \
    PredefinedCatalogViewSet, RecentList, FavoriteList, SignupView, FavoriteViewSet, SearchView

router = DefaultRouter()
router.register('recipes', RecipeViewSet, basename='recipe')
router.register('catalogs', CatalogViewSet, basename='catalog')
router.register('predefined-types', PredefinedCatalogTypeViewSet, basename='predefined-type')
router.register('predefined-catalogs', PredefinedCatalogViewSet, basename='predefined-catalog')
router.register('favorites', FavoriteViewSet, basename='favorite')

# recipes/urls.py
router.register('predefined-types', PredefinedCatalogTypeViewSet, basename='predefinedtype')
router.register('predefined-catalogs', PredefinedCatalogViewSet, basename='predefinedcatalog')
# urls.py

urlpatterns = [
    path('auth/signup/', SignupView.as_view(), name='auth_signup'),
    path('auth/login/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('auth/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('auth/logout/', TokenBlacklistView.as_view(), name='token_blacklist'),

    path('recent/', RecentList.as_view()),
    path("search/", SearchView.as_view(), name="search"),
    # path("favorites/", FavoriteList.as_view(), name="favorites"),


]
urlpatterns += router.urls
