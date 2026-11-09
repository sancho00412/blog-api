"""Fill the database with fake data: users, categories, tags, posts, comments.

Usage:
    python manage.py seed
    python manage.py seed --users 50 --posts 300 --comments 1500
    python manage.py seed --clear
"""

#Python modules
import random
import re
import time
from typing import Any

#Third party modules
from faker import Faker

#Django modules
from django.contrib.auth.hashers import make_password
from django.core.management.base import BaseCommand, CommandError, CommandParser
from django.db import transaction
from django.utils import timezone
from django.utils.text import slugify

#Project modules
from apps.auths.models import User
from apps.blog.constants import FIRST_SLUG_SUFFIX, POST_SLUG_MAX_LENGTH, SLUG_SUFFIX_TEMPLATE
from apps.blog.models import Category, Comment, Post, Tag

#-------------------------------------------------------------------------------------------
#Defaults for the command arguments
#
DEFAULT_USERS: int = 20
DEFAULT_POSTS: int = 100
DEFAULT_COMMENTS: int = 500

#-------------------------------------------------------------------------------------------
#Users
#
SEED_PASSWORD: str = "seedpass123"
EMAIL_DOMAINS: tuple[str, ...] = ("example.com", "blog.kz", "mail.com")
EMAIL_TAMPLATE: str = "{first}.{last}{number}@{domain}"
INACTIVE_USERS_RATIO: float = 0.15
STAFF_USERS_RATIO : float = 0.05
DATE_JOINED_START: str = "-2y"

#-------------------------------------------------------------------------------------------
#categories and tags
#
CATEGORY_NAMES: tuple[str, ...] = (
    "Python",
    "Django",
    "DevOps",
    "Databases",
    "Frontend",
    "Machine Learning",
    "Security",
    "Career",
)

TAG_NAMES: tuple [str, ...] = (
    "python3",
    "django-orm",
    "rest-api",
    "docker",
    "kubernetes",
    "postgresql",
    "redis",
    "celery",
    "testing",
    "pytest",
    "git",
    "linux",
    "javascript",
    "react",
    "css",
    "jwt",
    "performance",
    "tutorial",
    "beginners",
    "best-practices",
)

#-------------------------------------------------------------------------------------------
#Posts
#
PUBLISHED_POSTS_RATIO: float = 0.7
POSTS_WITHOUT_CATEGORY_RATIO: float = 0.1
MIN_TAGS_PER_POST: int = 0
MAX_TAGS_PER_POST: int = 5
MIN_TITLE_WORDS: int = 3
MAX_TITLE_WORDS: int = 8
MIN_PARAGRAPHS: int = 3
MAX_PARAGRAPHS: int = 6
PARAGRAPHS_SEPARRATOR: str = "\n\n"
TITLE_END_CHAR: str = "."

#-------------------------------------------------------------------------------------------
#Comments
#
MIN_COMMENT_SENTENCES: int = 1
MAX_COMMENT_SENTENCES: int = 3

#-------------------------------------------------------------------------------------------
#Other
#
BULK_BATCH_SIZE: int = 500
SUMMARY_LABEL_WIDTH: int = 11
SUMMARY_NUMBER_WITH: int = 5
NOT_LETTERS_PATTERN: re.Pattern[str] = re.compile(r"[^a-z0-9]")


class Command(BaseCommand):
    """Management command 'seed' ."""
    help = "Fill the database with fake data."
    def __init__(self, *args: Any, **kwargs: Any) -> None:
        super().__init__(*args, **kwargs)
        self.fake: Faker = Faker()

#-------------------------------------------------------------------------------------------
#Arguments
#
    def add_arguments(self, parser: CommandParser) -> None:
        parser.add_argument(
            "--users", type=int, default=DEFAULT_USERS, help="Number of users to create"
        )
        parser.add_argument(
            "--posts", type=int, default=DEFAULT_POSTS, help="Number of posts to create"
        )
        parser.add_argument(
            "--comments",
            type=int, 
            default=DEFAULT_COMMENTS,
            help="Number of comments to crate",
        )
        parser.add_argument(
            "--clear", action="store_true", help="delete existing data before seeding"
        )


    #-------------------------------------------------------------------------------------------
    #Entry point
    #
    def handle(self, *args: Any, **options: Any) -> None:
        users_count: int = options["users"]
        posts_count: int = options["posts"]
        comments_count: int = options["comments"]
        clear: bool = options["clear"]

        self._validate_numbers(users=users_count, posts= posts_count, comments=comments_count)

        start_time: float = time.perf_counter()

        #One transaction: if something fails, nothing is saved.
        with transaction.atomic():
            if clear:
                self._clear_data()

            users: list[User] = self._create_users(users_count)
            categories: list[Category] = self._create_categories()
            tags: list[Tag] = self._create_tags()
            posts: list[Post] = self._create_posts(posts_count)
            self._attach_tags(posts)
            comments: list[Comment] = self._create_comments(comments_count)

        elapsed: float = time.perf_counter() - start_time

        if clear:
            self.stdout.write(self.style.WARNING("Old data deleted(superusers are kept)."))

        self._print_summary(
            users=len(users),
            categories=len(categories),
            tags=len(tags),
            posts=len(posts),
            comments=len(comments),
            elapsed=elapsed
        )




    #-------------------------------------------------------------------------------------------
    #validation
    #
    def _validate_numbers(self, **numbers: int) -> None:
        """Raise CommandError if any number is negaive."""
        for name, value in numbers.items():
            if value < 0:
                raise CommandError(f"--{name} must be 0 or more, got {value}.")

    #-------------------------------------------------------------------------------------------
    #Clear
    #
    def _clear_data(self) -> None:
        """delete al blog data and all users except superusers."""
        Comment.objects.all().delete()
        Post.objects.all().delete()
        Tag.objects.all().delete()
        Category.objects.all().delete()
        User.objects.filter(is_superuser=False).delete()

    #-------------------------------------------------------------------------------------------
    #Users
    #
    def _create_users(self, count: int) -> list[User]:
        """Create users with unique emails and one shared hashes password."""
        if count == 0:
            return[]
        #Hashing is slow on purpose, so we do it only once.
        hashed_password:str = make_password(SEED_PASSWORD)
        used_emails: set[str] = set(User.objects.values_list("email", flat=True))

        users: list[User] = []
        for _ in range(count):
            first_name: str = self.fake.first_name()
            last_name: str = self.fake.last_name()
            email: str = self._unique_email(first_name, last_name, used_emails)
            used_emails.add(email)

            users.append(
                User(
                    email=email,
                    first_name=first_name,
                    last_name=last_name,
                    password=hashed_password,
                    is_active=random.random() >= INACTIVE_USERS_RATIO,
                    is_staff=random.random() < STAFF_USERS_RATIO,
                    date_joined=self.fake.date_time_between(
                        start_date=DATE_JOINED_START,
                        tzinfo=timezone.get_current_timezone(),
                    ),
                )
            )
        return User.objects.bulk_create(users, batch_size=BULK_BATCH_SIZE)

    def _unique_email(self,first_name: str, last_name: str, used_emails: set[str]) -> str:
        """Build an email from the last name. Add a number if it is already used."""
        first: str = NOT_LETTERS_PATTERN.sub("", first_name.lower())
        last: str = NOT_LETTERS_PATTERN.sub("", last_name.lower())
        domain: str = random.choice(EMAIL_DOMAINS)

        email: str = EMAIL_TAMPLATE.format(first=first, last=last, number="",domain=domain)
        number: int = FIRST_SLUG_SUFFIX
        while email in used_emails:
            email = EMAIL_TAMPLATE.format(first=first, last=last, number=number,domain=domain)
            number += 1
        return email




    #-------------------------------------------------------------------------------------------
    #Categories and tags
    #
    def _create_categories(self) -> list[Category]:
        """Create categories from CATEGORY_NAMES. Skip existing ones."""
        existing: set[str] = set(Category.objects.values_list("name", flat=True))
        new_categories: list[Category] = [
            Category(name=name, slug=slugify(name))
            for name in CATEGORY_NAMES
            if name not in existing
        ]
        return Category.objects.bulk_create(new_categories)

    def _create_tags(self) -> list[Tag]:
        """Create tags from TAG_NAMES. Skip existing ones."""
        existing: set[str] = set(Tag.objects.values_list("name", flat=True))
        new_tags: list[Tag] = [
            Tag(name=name, slug=slugify(name)) for name in TAG_NAMES if name not in existing
        ]
        return Tag.objects.bulk_create(new_tags)

    #-------------------------------------------------------------------------------------------
    #Posts
    #
    def _create_posts(self, count: int) -> list[Post]:
        """Create posts with unique slugs, ramdom author, status and category."""
        if count == 0:
            return []
        author_ids: list[int] = list(User.objects.values_list("pk", flat=True))
        if not author_ids:
            raise CommandError("Cannot create posts: there are no users. Use --users.")
        categories: list[Category] = list(Category.objects.all())
        used_slugs: set[str] = set(Post.objects.values_list("slug", flat=True))

        posts: list[Post] = []
        for _ in range(count):
            title: str = self._fake_title()
            slug: str = self._unique_slug(title, used_slugs)
            used_slugs.add(slug)

            is_published: bool = random.random() < PUBLISHED_POSTS_RATIO
            has_category: bool = bool(categories) and (
                random.random() >= POSTS_WITHOUT_CATEGORY_RATIO
            )

            posts.append(
                Post(
                    author_id=random.choice(author_ids),
                    title=title,
                    #bulk_create does not call save(), so we set the slug ourselves.
                    slug=slug,
                    body=PARAGRAPHS_SEPARRATOR.join(
                        self.fake.paragraphs(nb=random.randint(MIN_PARAGRAPHS,MAX_PARAGRAPHS))
                    ),
                    category=random.choice(categories) if has_category else None,
                    status=Post.Status.PUBLISHED if is_published else Post.Status.DRAFT
                )
            )
        return Post.objects.bulk_create(posts, batch_size=BULK_BATCH_SIZE)

    def _fake_title(self) -> str:
        """Return a short sentence without the dot at the end."""
        words: int = random.randint(MIN_TITLE_WORDS, MAX_TITLE_WORDS)
        sentence: str = self.fake.sentence(nb_words=words, variable_nb_words=False)
        return sentence.rstrip(TITLE_END_CHAR)

    @staticmethod
    def _unique_slug(title: str, used_slugs: set[str]) -> str:
        """Return my-post, or my-post-2, my-post-3 ... if the slug is taken."""
        base_slug: str = slugify(title)[:POST_SLUG_MAX_LENGTH]
        slug: str = base_slug
        number: int = FIRST_SLUG_SUFFIX
        while slug in used_slugs:
            slug = SLUG_SUFFIX_TEMPLATE.format(slug=base_slug, number=number)
            number += 1
        return slug

    def _attach_tags(self, posts: list[Post]) -> None:
        """Give every new post from 0 to 5 random tags."""
        tags: list[Tag] = list(Tag.objects.all())
        if not tags:
            return

        max_tags: int = min(MAX_TAGS_PER_POST, len(tags))
        for post in posts:
            # After bulk_create the posts have ids, so .set() words.
            post.tags.set(random.sample(tags, k=random.randint(MIN_TAGS_PER_POST,max_tags)))

    def _create_comments(self, count: int) -> list[Comment]:
        if count == 0:
            return []
        author_ids: list[int] = list(User.objects.values_list("pk", flat=True))
        if not author_ids:
            raise CommandError("No users. Use --users.")
        post_ids: list[int] = list(
            Post.objects.filter(status=Post.Status.PUBLISHED).values_list("pk", flat=True)
        )
        if not post_ids:
            raise CommandError("No published posts. Use --posts.")
        comments: list[Comment] = [
            Comment(
                post_id=random.choice(post_ids),
                author_id=random.choice(author_ids),
                body=" ".join(
                    self.fake.sentences(random.randint(MIN_COMMENT_SENTENCES,MAX_COMMENT_SENTENCES))
                ),
            )
            for _ in range(count)
        ]
        return Comment.objects.bulk_create(comments, batch_size=BULK_BATCH_SIZE)

    def _print_summary(self, elapsed: float, **counts: int) -> None:
            for label, number in counts.items():
                self.stdout.write(f"{label.capitalize()}: {number} created")
            self.stdout.write(self.style.SUCCESS(f"Done in {elapsed:.2f} seconds"))