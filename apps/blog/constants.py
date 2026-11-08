"""Constants for the blog app."""

CATEGORY_NAME_MAX_LENGTH: int = 100
TAG_NAME_MAX_LENGTH: int = 50
POST_TITLE_MAX_LENGTH: int = 200
POST_STATUS_MAX_LENGTH: int = 20

# Length of the slug field (SlugField default is 50, titles can be longer).
POST_SLUG_MAX_LENGTH: int = 220

# Suffix pattern for duplicate slugs: my-post, my-post-2, my-post-3 ...
SLUG_SUFFIX_TEMPLATE: str = "{slug}-{number}"
FIRST_SLUG_SUFFIX: int = 2

# How many characters of a comment are shown in __str__.
COMMENT_PREVIEW_LENGTH: int = 30
