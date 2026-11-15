import json
from typing import Any

from django.conf import settings
from django.db.models import Count, Q
from django.http import HttpRequest

from apps.auths.models import User
from apps.blog.models import Category, Comment, Post


def environment_callback(request: HttpRequest) -> list[str]:
    if settings.ENV_ID == "local":
        return ["Local", "warning"]
    return ["Production", "danger"]


def drafts_badge(request: HttpRequest) -> str:
    return str(Post.objects.filter(status=Post.Status.DRAFT).count())


def is_superuser(request: HttpRequest) -> bool:
    return request.user.is_superuser


TOP_AUTHORS_LIMIT: int = 5
PERCENT: int = 100


def dashboard_callback(request: HttpRequest, context: dict[str, Any]) -> dict[str, Any]:
    counts: dict[str, int] = Post.objects.aggregate(
        total=Count("pk"),
        published=Count("pk", filter=Q(status=Post.Status.PUBLISHED)),
        drafts=Count("pk", filter=Q(status=Post.Status.DRAFT)),
    )
    categories = Category.objects.annotate(posts_total=Count("posts")).order_by("name")
    authors = User.objects.annotate(posts_total=Count("posts")).order_by("-posts_total")[
        :TOP_AUTHORS_LIMIT
    ]
    published_percent: int = (
        round(counts["published"] * PERCENT / counts["total"]) if counts["total"] else 0
    )

    context.update(
        {
            "cards": [
                {"title": "Users", "value": User.objects.count()},
                {"title": "Published posts", "value": counts["published"]},
                {"title": "Drafts", "value": counts["drafts"]},
                {"title": "Comments", "value": Comment.objects.count()},
            ],
            "chart": json.dumps(
                {
                    "labels": [c.name for c in categories],
                    "datasets": [{"label": "Posts", "data": [c.posts_total for c in categories]}],
                }
            ),
            "table": {
                "headers": ["Author", "Email", "Posts"],
                "rows": [[a.get_full_name(), a.email, a.posts_total] for a in authors],
            },
            "published_percent": published_percent,
            "drafts_percent": PERCENT - published_percent if counts["total"] else 0,
        }
    )
    return context
