"""Run the ORM queries ans show the result and the number of SQL queries"""

from datetime import timedelta
from typing import Any

from django.core.management.base import BaseCommand, CommandError, CommandParser
from django.db import connection
from django.db.models import Model, QuerySet
from django.test.utils import CaptureQueriesContext
from django.utils import timezone

from apps.auths.models import User
from apps.blog.models import Post
from apps.blog.queries import QUERIES

ROWS_TO_SHOW: int = 5
CHANGING_QUERIES: range = range(40, 45)
DAYS_BACK: int = 30


def sample_arguments() -> dict[int, dict[str, Any]]:
    """Sample arguments for queries that need them."""
    today = timezone.localdate()
    email: str = User.objects.filter(posts__isnull=False).values_list("email", flat=True).first()
    slug: str = Post.objects.values_list("slug", flat=True).first()
    first_name: str = User.objects.values_list("first_name", flat=True).first()
    return {
        4: {"slug": slug},
        7: {"page": 1},
        8: {"word": "the"},
        9: {"domain": "example.com"},
        11: {"slugs": ["python", "django"]},
        12: {"year": today.year, "month": today.month},
        13: {"days": DAYS_BACK},
        14: {"start": today - timedelta(days=DAYS_BACK), "end": today},
        15: {"email": email},
        16: {"tag_slug": "docker"},
        17: {"category_slug": "python"},
        21: {"first_slug": "docker", "second_slug": "git"},
        22: {"text": "the"},
        34: {"min_posts": 10},
        37: {"text": first_name},
        40: {"name": "Django ORM"},
        41: {"days": DAYS_BACK},
        42: {"category_slug": "python", "tag_slug": "docker"},
        43: {"source_slug": "career", "target_slug": "python"},
    }


class Command(BaseCommand):
    """Management command 'queries'."""

    help = "Run the ORM queries from apps/blog/queries.py"

    def add_arguments(self, parser: CommandParser) -> None:
        parser.add_argument("--number", type=int, help="Run only this query")
        parser.add_argument("--sql", action="store_true", help="Print the SQL")

    def handle(self, *args, **options: Any) -> None:
        number: int | None = options["number"]
        if number is not None and number not in QUERIES:
            raise CommandError(f"Query #{number} does not exists.")

        numbers: list[int] = (
            [number] if number else [n for n in QUERIES if n not in CHANGING_QUERIES]
        )
        arguments: dict[int, dict[str, Any]] = sample_arguments()
        for n in numbers:
            self._run(n, arguments.get(n, {}), options["sql"])

    def _run(self, number: int, arguments: dict[str, Any], show_sql: bool) -> None:
        function = QUERIES[number]
        with CaptureQueriesContext(connection) as context:
            result: Any = function(**arguments)
            annotations: list[str] = []
            if isinstance(result, QuerySet):
                annotations = list(result.query.annotations)
                result = list(result)

        count: int = len(context.captured_queries)
        word: str = "query" if count == 1 else "queries"
        self.stdout.write(self.style.SUCCESS(f"#{number} {function.__name__} - {count} SQL {word}"))
        if show_sql:
            for query in context.captured_queries:
                self.stdout.write(query["sql"])
        self._print_result(result, annotations)

    def _print_result(self, result: Any, annotations: list[str]) -> None:
        if isinstance(result, dict) and all(isinstance(v, list) for v in result.values()):
            result = list(result.items())
        if not isinstance(result, list):
            self.stdout.write(f"  {result}")
            return
        for row in result[:ROWS_TO_SHOW]:
            if isinstance(row, Model) and annotations:
                values = {name: getattr(row, name) for name in annotations}
                self.stdout.write(f"  {row} {values}")
            else:
                self.stdout.write(f"  {row}")
        self.stdout.write(f"  ({len(result)} rows)")
