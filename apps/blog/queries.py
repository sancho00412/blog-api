"""50 ORM queries for Home Work 3."""

from collections.abc import Callable
from datetime import date, timedelta
from typing import Any

from django.db import transaction
from django.db.models import(
    Avg,
    Case,
    Count,
    Exists,
    F,
    Max,
    Min,
    OuterRef,
    Prefetch,
    Q,
    QuerySet,
    Subquery,
    Value,
    When,
)
from django.db.models.functions import Coalesce, Concat, TruncMonth
from django.utils import timezone
from django.utils.text import slugify

from apps.auths.models import User
from apps.blog.models import Category, Comment, Post, Tag

PUBLISHED: str = Post.Status.PUBLISHED
DRAFT: str = Post.Status.DRAFT
NEWEST_POSTS_LIMIT: int = 5
PAGE_SIZE: int = 10
EDIT_THRESHOLD: timedelta = timedelta
UNCATEGORIZED: str = "Uncategorized"
TOP_AUTHORS_LIMIT: int = 5
HOT_COMMENTS: int = 10
NORMAL_COMMENTS: int = 3
AVERAGE_DIGITS: int = 2
FEED_LIMIT: int = 50
NEWEST_WITH_TAGS_LIMIT: int = 20

def categories_by_name() -> QuerySet[Category]:
    """All Categories, A -> Z."""
    return Category.objects.order_by("name")

def published_posts() ->  QuerySet[Post]:
    """Published posts, newest first."""
    return Post.objects.filter(status=PUBLISHED).order_by("-created_at")

def newest_published_posts() ->QuerySet[Post]:
    """The 5 newest published posts."""
    return published_posts()[:NEWEST_POSTS_LIMIT]

def post_by_slug(slug: str) -> Post | None:
    """The post with this slag or None."""
    return Post.objects.filter(slug=slug).first()

def active_users_count() -> int:
    """Number of active users that are not staff."""
    return User.objects.filter(is_active=True, is_staff= False).count()

def has_drafts() -> bool:
    """True if there is at least one draft."""
    return Post.objects.filter(status=DRAFT).exists()

def published_posts_page(page: int) -> QuerySet[Post]:
    """One page of published posts, 10 per page."""
    start: int = (page - 1) * PAGE_SIZE
    return published_posts()[start : start + PAGE_SIZE]

QUERIES: dict[int, Callable[..., Any]] ={
    1: categories_by_name,
    2: published_posts,
    3: newest_published_posts,
    4: post_by_slug,
    5: active_users_count,
    6: has_drafts,
    7: published_posts_page
}