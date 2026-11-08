# Django modules
from django.conf import settings
from django.db.models import (
    CASCADE,
    SET_NULL,
    CharField,
    DateTimeField,
    ForeignKey,
    ManyToManyField,
    Model,
    SlugField,
    TextChoices,
    TextField,
)
from django.utils.text import slugify

# Project modules
from apps.blog.constants import (
    CATEGORY_NAME_MAX_LENGTH,
    COMMENT_PREVIEW_LENGTH,
    FIRST_SLUG_SUFFIX,
    POST_SLUG_MAX_LENGTH,
    POST_STATUS_MAX_LENGTH,
    POST_TITLE_MAX_LENGTH,
    SLUG_SUFFIX_TEMPLATE,
    TAG_NAME_MAX_LENGTH,
)


class Category(Model):
    """Post category, e.g. Python or Django."""

    name = CharField(max_length=CATEGORY_NAME_MAX_LENGTH, unique=True)
    slug = SlugField(unique=True)

    class Meta:
        verbose_name = "category"
        verbose_name_plural = "categories"
        ordering = ("name",)

    def __str__(self) -> str:
        return self.name

    def save(self, *args: object, **kwargs: object) -> None:
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)


class Tag(Model):
    """Post tag. A post can have many tags."""

    name = CharField(max_length=TAG_NAME_MAX_LENGTH, unique=True)
    slug = SlugField(unique=True)

    class Meta:
        verbose_name = "tag"
        verbose_name_plural = "tags"
        ordering = ("name",)

    def __str__(self) -> str:
        return self.name

    def save(self, *args: object, **kwargs: object) -> None:
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)


class Post(Model):
    """Blog post."""

    class Status(TextChoices):
        DRAFT = "draft", "Draft"
        PUBLISHED = "published", "Published"

    author = ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=CASCADE,
        related_name="posts",
    )
    title = CharField(max_length=POST_TITLE_MAX_LENGTH)
    slug = SlugField(max_length=POST_SLUG_MAX_LENGTH, unique=True)
    body = TextField()
    category = ForeignKey(
        Category,
        on_delete=SET_NULL,
        null=True,
        blank=True,
        related_name="posts",
    )
    tags = ManyToManyField(Tag, blank=True, related_name="posts")
    status = CharField(
        max_length=POST_STATUS_MAX_LENGTH,
        choices=Status.choices,
        default=Status.DRAFT,
    )
    created_at = DateTimeField(auto_now_add=True)
    updated_at = DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "post"
        verbose_name_plural = "posts"
        ordering = ("-created_at",)

    def __str__(self) -> str:
        return self.title

    def save(self, *args: object, **kwargs: object) -> None:
        if not self.slug:
            self.slug = self._generate_unique_slug()
        super().save(*args, **kwargs)

    def _generate_unique_slug(self) -> str:
        """Build a slug from the title. Add -2, -3 ... if it is taken."""
        base_slug: str = slugify(self.title)[:POST_SLUG_MAX_LENGTH]
        slug: str = base_slug
        number: int = FIRST_SLUG_SUFFIX
        while Post.objects.filter(slug=slug).exclude(pk=self.pk).exists():
            slug = SLUG_SUFFIX_TEMPLATE.format(slug=base_slug, number=number)
            number += 1
        return slug


class Comment(Model):
    """Comment on a post."""

    post = ForeignKey(Post, on_delete=CASCADE, related_name="comments")
    author = ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=CASCADE,
        related_name="comments",
    )
    body = TextField()
    created_at = DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "comment"
        verbose_name_plural = "comments"
        ordering = ("-created_at",)

    def __str__(self) -> str:
        return f"{self.author}: {self.body[:COMMENT_PREVIEW_LENGTH]}"
