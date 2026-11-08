# Django modules
from django.contrib import admin

# Project modules
from apps.blog.models import Category, Comment, Post, Tag


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ("name", "slug")
    search_fields = ("name",)
    prepopulated_fields = {"slug": ("name",)}


@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    list_display = ("name", "slug")
    search_fields = ("name",)
    prepopulated_fields = {"slug": ("name",)}


@admin.register(Post)
class PostAdmin(admin.ModelAdmin):
    list_display = ("title", "author", "status", "category", "created_at")
    list_filter = ("status", "category")
    search_fields = ("title", "body")
    prepopulated_fields = {"slug": ("title",)}
    filter_horizontal = ("tags",)
    list_select_related = ("author", "category")


@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    list_display = ("post", "author", "created_at")
    search_fields = ("body",)
    list_select_related = ("post", "author")
