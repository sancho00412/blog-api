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
EDIT_THRESHOLD: timedelta = timedelta(hours=1)

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

#-------------------Level 2---------------------
def posts_with_word_in_title(word: str) -> QuerySet[Post]:
    """Posts whose title contains the word, any case."""
    return Post.objects.filter(title__icontains=word)

def users_with_email_domain(domain: str) -> QuerySet[User]:
    """Users whose email ends with @domain."""
    return User.objects.filter(email__iendswith=f"@{domain}")

def posts_without_category() -> QuerySet[Post]:
    """Posts with no category."""
    return Post.objects.filter(category__isnull=True)

def categories_by_slugs(slugs: list[str]) -> QuerySet[Category]:
    """Categories whose slug is in the list."""
    return Category.objects.filter(slug__in=slugs)

def posts_in_months(year: int, month: int) -> QuerySet[Post]:
    """Posts created in this month"""
    return Post.objects.filter(created_at__year=year, created_at__month=month)

def posts_last_days(days: int) -> QuerySet[Post]:
    """Posts created in the last N days"""
    return Post.objects.filter(created_at__gte=timezone.now() - timedelta(days=days))

def posts_between(start: date, end: date) -> QuerySet[Post]:
    """Posts created from start tp end, both days included."""
    return Post.objects.filter(created_at__date__range=(start, end))

#-------------------Level 2---------------------
def author_published_posts(email:str) -> QuerySet[Post]:
    """Published posts of the author with this email."""
    return Post.objects.filter(author__email__iexact=email, status=PUBLISHED)

def posts_with_tag(tag_slug: str) -> QuerySet[Post]:
    """Posts that have this tag."""
    return Post.objects.filter(tags__slug=tag_slug)

def comments_in_category(category_slug: str) -> QuerySet[Comment]:
    """Comments on posts of this category."""
    return Comment.objects.filter(post__category__slug=category_slug)

def users_with_published_posts() -> QuerySet[User]:
    """Users with at least one published post, no repeats."""
    return User.objects.filter(posts__status=PUBLISHED).distinct()

def posts_without_tags() -> QuerySet[Post]:
    """Posts with no tags."""
    return Post.objects.filter(tags__isnull=True)

def users_without_comments() -> QuerySet[User]:
    """Users who never wrote a comment."""
    return User.objects.filter(comments__isnull=True)

def posts_with_both_tags(first_slug: str, second_slug: str) -> QuerySet[Post]:
    """Posts that have both tags."""
    return Post.objects.filter(tags__slug=first_slug).filter(tags__slug=second_slug)

#---------------------Level-4------------------------------------
def search_posts(text: str) -> QuerySet[Post]:
    """Posts with the text in the title or in the body."""
    return Post.objects.filter(Q(title__icontains=text) | Q(body__icontains=text))

def published_posts_missing_info() -> QuerySet[Post]:
    """Published posts with no category or no tags."""
    return(
        Post.objects.filter(status=PUBLISHED)
        .filter(Q(category__isnull=True) | Q(tags__isnull=True))
        .distinct()
    )

def edited_posts() -> QuerySet[Post]:
    """Posts edited more than 1 hours after creation."""
    return Post.objects.filter(updated_at__gt=F("created_at") + EDIT_THRESHOLD)

def comments_by_post_author() -> QuerySet[Comment]:
    """Comments written by the author of the post"""
    return Comment.objects.filter(author=F("post__author"))

def comments_before_post() -> QuerySet[Comment]:
    """Comments created before their post. Must be empty."""
    return Comment.objects.filter(created_at__lt=F("post__created_at"))

#---------------------Level-5------------------------------------
def published_authors_emails() -> list[str]:
    """Unique emails of authors with published posts, A -> Z."""
    return list(
        User.objects.filter(posts__status=PUBLISHED)
        .values_list("email", flat=True)
        .distinct()
        .order_by("email")
    )

def published_posts_overview() -> list[dict[str, Any]]:
    """Title, author email and category name of published posts."""
    return list(
        Post.objects.filter(status=PUBLISHED).values(
            "title",
            author_email=F("author__email"),
            category_name=Coalesce("category__name", Value(UNCATEGORIZED)),
        )
    )

QUERIES: dict[int, Callable[..., Any]] ={
    1: categories_by_name,
    2: published_posts,
    3: newest_published_posts,
    4: post_by_slug,
    5: active_users_count,
    6: has_drafts,
    7: published_posts_page,
    8: posts_with_word_in_title,
    9: users_with_email_domain,
    10: posts_without_category,
    11: categories_by_slugs,
    12: posts_in_months,
    13: posts_last_days,
    14: posts_between,
    15: author_published_posts,
    16: posts_with_tag,
    17: comments_in_category,
    18: users_with_published_posts,
    19: posts_without_tags,
    20: users_without_comments,
    21: posts_with_both_tags,
    22: search_posts,
    23: published_posts_missing_info,
    24: edited_posts,
    25: comments_by_post_author,
    26: comments_before_post,
    27: published_authors_emails,
    28: published_posts_overview
}

