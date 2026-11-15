from django.http import HttpRequest
from django.urls import reverse

STATUS_PARAM: str = "status__exact"


def published_link(request: HttpRequest) -> str:
    return reverse("admin:blog_post_changelist") + f"?{STATUS_PARAM}=published"


def drafts_link(request: HttpRequest) -> str:
    return reverse("admin:blog_post_changelist") + f"?{STATUS_PARAM}=draft"


def all_active(request: HttpRequest) -> bool:
    return STATUS_PARAM not in request.GET


def published_active(request: HttpRequest) -> bool:
    return request.GET.get(STATUS_PARAM) == "published"


def drafts_active(request: HttpRequest) -> bool:
    return request.GET.get(STATUS_PARAM) == "draft"