from unfold.admin import ModelAdmin, TabularInline
from unfold.contrib.filters.admin import (
    AutocompleteSelectFilter,
    ChoicesDropdownFilter,
    MultipleRelatedDropdownFilter,
    RangeDateTimeFilter,
    RelatedDropdownFilter,
)
from unfold.contrib.forms.widgets import WysiwygWidget
from unfold.decorators import action, display
from unfold.enums import ActionVariant
from unfold.sections import TableSection

from django.contrib import admin
from django.db.models import Count, Prefetch, QuerySet, TextField
from django.http import HttpRequest, HttpResponse
from django.shortcuts import redirect
from django.urls import reverse
from django.utils.text import Truncator

from apps.blog.models import Category, Comment, Post, Tag

COMMENT_PREVIEW_LENGTH: int = 60
COMMENTS_PER_PAGE: int = 10
STATUS_COLORS: dict[str, str] = {Post.Status.PUBLISHED: "success", Post.Status.DRAFT: "warning"}
TAB: list[str] = ["tab"]


class CategoryPostsSection(TableSection):
    verbose_name = "Posts"
    related_name = "posts"
    fields = ["title", "author", "status"]


class NameAdmin(ModelAdmin):
    list_display = ["name", "slug", "posts_count"]
    search_fields = ["name"]
    prepopulated_fields = {"slug": ("name",)}

    def get_queryset(self, request: HttpRequest) -> QuerySet:
        return super().get_queryset(request).annotate(posts_total=Count("posts"))

    @display(description="Posts", ordering="posts_total")
    def posts_count(self, obj: Category | Tag) -> int:
        return obj.posts_total


@admin.register(Tag)
class TagAdmin(NameAdmin):
    pass


@admin.register(Category)
class CategoryAdmin(NameAdmin):
    list_sections = [CategoryPostsSection]

    def get_queryset(self, request: HttpRequest) -> QuerySet:
        return super().get_queryset(request).prefetch_related("posts__author")


class PostCommentsSection(TableSection):
    verbose_name = "Comments"
    related_name = "comments"
    fields = ["author", "body", "created_at"]


class CommentInline(TabularInline):
    model = Comment
    fields = ["author", "body", "created_at"]
    readonly_fields = ["created_at"]
    autocomplete_fields = ["author"]
    extra = 0
    tab = True
    per_page = COMMENTS_PER_PAGE


@admin.register(Post)
class PostAdmin(ModelAdmin):
    list_display = [
        "post_header",
        "status_label",
        "category",
        "tags_dropdown",
        "comments_count",
        "created_at",
    ]
    list_filter = [
        ("status", ChoicesDropdownFilter),
        ("category", RelatedDropdownFilter),
        ("tags", MultipleRelatedDropdownFilter),
        ("author", AutocompleteSelectFilter),
        ("created_at", RangeDateTimeFilter),
    ]
    list_filter_submit = True
    search_fields = ["title", "body", "author__email"]
    list_sections = [PostCommentsSection]

    actions = ["publish_selected", "move_to_drafts"]
    actions_row = ["toggle_status"]
    actions_list = ["publish_all_drafts"]
    actions_detail = ["open_comments"]
    actions_submit_line = ["save_and_publish"]

    fieldsets = [
        ("Content", {"classes": TAB, "fields": ["title", "slug", "body"]}),
        ("Classification", {"classes": TAB, "fields": ["category", "tags", "status"]}),
        ("Meta", {"classes": TAB, "fields": ["author", "created_at", "updated_at"]}),
    ]
    prepopulated_fields = {"slug": ("title",)}
    autocomplete_fields = ["author", "category", "tags"]
    readonly_fields = ["created_at", "updated_at"]
    formfield_overrides = {TextField: {"widget": WysiwygWidget}}
    warn_unsaved_form = True
    inlines = [CommentInline]

    def get_queryset(self, request: HttpRequest) -> QuerySet:
        return (
            super()
            .get_queryset(request)
            .select_related("author", "category")
            .prefetch_related(
                "tags", Prefetch("comments", Comment.objects.select_related("author"))
            )
            .annotate(comments_total=Count("comments", distinct=True))
            .order_by("-created_at")
        )

    @display(description="Post", header=True, ordering="title")
    def post_header(self, obj: Post) -> list[str]:
        return [obj.title, obj.author.email]

    @display(description="Status", label=STATUS_COLORS)
    def status_label(self, obj: Post) -> tuple[str, str]:
        return obj.status, obj.get_status_display()

    @display(description="Tags", dropdown=True)
    def tags_dropdown(self, obj: Post) -> dict:
        tags: list[Tag] = list(obj.tags.all())
        return {
            "title": f"{len(tags)} tags",
            "items": [{"title": tag.name} for tag in tags],
        }

    @display(description="Comments", ordering="comments_total")
    def comments_count(self, obj: Post) -> int:
        return obj.comments_total

    @action(description="Publish selected")
    def publish_selected(self, request: HttpRequest, queryset: QuerySet) -> None:
        queryset.update(status=Post.Status.PUBLISHED)

    @action(description="Move to drafts")
    def move_to_drafts(self, request: HttpRequest, queryset: QuerySet) -> None:
        queryset.update(status=Post.Status.DRAFT)

    @action(description="Publish / unpublish", permissions=["change"])
    def toggle_status(self, request: HttpRequest, object_id: int) -> HttpResponse:
        post: Post = Post.objects.get(pk=object_id)
        if post.status == Post.Status.PUBLISHED:
            post.status = Post.Status.DRAFT
        else:
            post.status = Post.Status.PUBLISHED
        post.save()
        return redirect(request.headers.get("referer") or reverse("admin:blog_post_changelist"))

    @action(description="Publish all drafts", permissions=["change"], variant=ActionVariant.PRIMARY)
    def publish_all_drafts(self, request: HttpRequest) -> HttpResponse:
        Post.objects.filter(status=Post.Status.DRAFT).update(status=Post.Status.PUBLISHED)
        return redirect(reverse("admin:blog_post_changelist"))

    @action(description="Open comments")
    def open_comments(self, request: HttpRequest, object_id: int) -> HttpResponse:
        url: str = reverse("admin:blog_comment_changelist")
        return redirect(f"{url}?post__id__exact={object_id}")

    @action(description="Save & publish", permissions=["change"])
    def save_and_publish(self, request: HttpRequest, obj: Post) -> None:
        obj.status = Post.Status.PUBLISHED
        obj.save()


@admin.register(Comment)
class CommentAdmin(ModelAdmin):
    list_display = ["post__title", "author", "short_body", "created_at"]
    list_select_related = ["post", "author"]
    list_filter = [
        ("post", AutocompleteSelectFilter),
        ("author", AutocompleteSelectFilter),
        ("created_at", RangeDateTimeFilter),
    ]
    list_filter_submit = True
    search_fields = ["body", "author__email", "post__title"]
    autocomplete_fields = ["post", "author"]

    @display(description="Comment")
    def short_body(self, obj: Comment) -> str:
        return Truncator(obj.body).chars(COMMENT_PREVIEW_LENGTH)
