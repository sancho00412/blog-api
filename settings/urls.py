"""Root URL configuration."""

# Django modules
from django.contrib import admin
from django.urls import URLPattern, URLResolver, include, path

urlpatterns: list[URLPattern | URLResolver] = [
    path("admin/", admin.site.urls),
    path("api/auth/", include("apps.auths.urls")),
]
