"""data_generators.py
====================

Type‑safe, reproducible factories that generate valid **and** intentionally
invalid payloads for typical REST resources — users, posts and comments.
The public API is minimal: call the generator to get a `dict`; flip
`invalid=True` or pass an `error_type` Enum to corrupt the data.

---
Quick usage guide

from data_generators import (
    set_seed, RandomUser, RandomPost, RandomComment,
    CommonError, EmailError,
)

0)  Make results deterministic (optional)
set_seed(42)

1)  A valid user payload
user_gen = RandomUser()
user_payload = user_gen()  # same as user_gen(invalid=False)

2)  Same user but with an invalid e‑mail address
bad_user = user_gen(invalid=True, error_type=EmailError.INVALID)

3)  Valid post for that user (requires user_id)
post_gen = RandomPost()
post_payload = post_gen(parent_id=123)

4)  Post with *two* title errors: empty + too long
broken_post = post_gen(
    parent_id=123,
    invalid=True,
    error_type=[CommonError.EMPTY, CommonError.TOO_LONG],
)

5)  Comment with an overridden body and invalid e‑mail
comment_gen = RandomComment()
comment_payload = comment_gen(
    parent_id=999,
    invalid=True,
    error_type=EmailError.INVALID,
    body="Great article!",  # override field on the fly
)

6)  Typical pytest parametrisation
import pytest

@pytest.mark.parametrize(
    "comment_data",
    [
        RandomComment()(parent_id=1),  # valid
        RandomComment()(parent_id=1, invalid=True, error_type=CommonError.EMPTY),
        RandomComment()(parent_id=1, invalid=True, error_type=EmailError.INVALID),
    ],
)
def test_create_comment(api_client, comment_data):
    resp = api_client.create_comment(comment_data)
    assertions
"""

from __future__ import annotations

import random
from abc import ABC, abstractmethod
from copy import deepcopy
from dataclasses import dataclass
from enum import Enum, auto
from typing import Any, Callable, List, Mapping, Optional, Union

from faker import Faker

# ---------------------------------------------------------------------------
# Shared Faker instance — cheaper and reproducible
# ---------------------------------------------------------------------------
_FAKER = Faker()


def set_seed(seed: int) -> None:
    """Seed both *random* and *Faker* for deterministic output."""

    Faker.seed(seed)
    random.seed(seed)


# ---------------------------------------------------------------------------
# Error enums
# ---------------------------------------------------------------------------
class CommonError(Enum):
    EMPTY = auto()
    TOO_LONG = auto()
    NONE = auto()


class EmailError(Enum):
    INVALID = auto()
    NONE = auto()


# ---------------------------------------------------------------------------
# Base contract
# ---------------------------------------------------------------------------
class DataGenerator(ABC):
    """All concrete generators must implement the same surface."""

    @abstractmethod
    def valid(self, parent_id: Optional[int] = None) -> dict:  # noqa: D401
        """Return a valid payload.

        :param parent_id: Foreign‑key value if the resource is nested.
        """

    @abstractmethod
    def invalid(
            self,
            parent_id: Optional[int] = None,
            error_type: Union[Enum, List[Enum], None] = None,
    ) -> dict:
        """Return a payload corrupted according to *error_type*."""

    @abstractmethod
    def __call__(
            self,
            parent_id: Optional[int] = None,
            *,
            invalid: bool = False,
            error_type: Union[Enum, List[Enum], None] = None,
            **overrides: Any,
    ) -> dict:
        """Unified entry‑point for tests.

        ``overrides`` let you tweak any field on the fly.
        """


# ---------------------------------------------------------------------------
# Re‑usable mixin for error injection
# ---------------------------------------------------------------------------
class ErrorInjectionMixin:
    @staticmethod
    def _ensure_iter(value: Union[Enum, List[Enum]]) -> List[Enum]:
        return [value] if isinstance(value, Enum) else list(value)

    def inject_error(
            self,
            data: dict[str, Any],
            error_type: Union[Enum, List[Enum]],
            mapping: Mapping[Enum, tuple[str, Any]],
    ) -> dict:
        """Return a *copy* of *data* with corrupted values applied."""

        corrupted = deepcopy(data)
        for err in self._ensure_iter(error_type):
            if err not in mapping:
                raise ValueError(f"Unknown error_type: {err!r}")
            field, bad_value = mapping[err]
            corrupted[field] = bad_value
        return corrupted


# ---------------------------------------------------------------------------
# Field variant helper
# ---------------------------------------------------------------------------
@dataclass(slots=True)
class FieldVariant:
    fake_func: Callable[[], str]
    max_len: int = 200

    @property
    def valid(self) -> str:
        return self.fake_func()

    @property
    def empty(self) -> str:  # noqa: D401
        return ""

    @property
    def too_long(self) -> str:  # noqa: D401
        return "A" * self.max_len * 3

    @property
    def none(self) -> None:  # noqa: D401
        return None


# ---------------------------------------------------------------------------
# Concrete generators
# ---------------------------------------------------------------------------
class RandomPost(DataGenerator, ErrorInjectionMixin):
    """Factory for *posts* (belongs to a user)."""

    def __init__(
            self,
            title_variant: FieldVariant | None = None,
            body_variant: FieldVariant | None = None,
    ) -> None:
        self.title = title_variant or FieldVariant(lambda: _FAKER.sentence(nb_words=6))
        self.body = body_variant or FieldVariant(lambda: _FAKER.text(max_nb_chars=200))

    # ------------------------------------------------------------------ valid
    def valid(self, parent_id: Optional[int] = None) -> dict:
        if parent_id is None:
            raise ValueError("Post requires a user_id (parent_id).")
        return {
            "user_id": parent_id,
            "title": self.title.valid,
            "body": self.body.valid,
        }

    # ---------------------------------------------------------------- invalid
    def invalid(
            self,
            parent_id: Optional[int] = None,
            error_type: Union[CommonError, List[CommonError], None] = None,
    ) -> dict:
        error_type = error_type or CommonError.EMPTY
        mapping = {
            CommonError.EMPTY: ("title", self.title.empty),
            CommonError.TOO_LONG: ("title", self.title.too_long),
            CommonError.NONE: ("title", self.title.none),
        }
        return self.inject_error(self.valid(parent_id), error_type, mapping)

    # ------------------------------------------------------------- callable
    def __call__(
            self,
            parent_id: Optional[int] = None,
            *,
            invalid: bool = False,
            error_type: Union[CommonError, List[CommonError], None] = None,
            **overrides: Any,
    ) -> dict:
        payload = (
            self.invalid(parent_id, error_type) if invalid else self.valid(parent_id)
        )
        payload.update(overrides)
        return payload


class RandomUser(DataGenerator, ErrorInjectionMixin):
    """Factory for users."""

    def __init__(self, email_variant: FieldVariant | None = None) -> None:
        gender = random.choice(["male", "female"])
        first = (
            _FAKER.first_name_male() if gender == "male" else _FAKER.first_name_female()
        )
        last = (
            _FAKER.last_name_male() if gender == "male" else _FAKER.last_name_female()
        )
        self._name = f"{first} {last}"
        self._gender = gender
        self._status = "active" if random.random() < 0.9 else "inactive"
        self.email = email_variant or FieldVariant(lambda: self._auto_email())

    def _auto_email(self) -> str:
        return f"{self._name.replace(' ', '.').lower()}@example.com"

    # ------------------------------------------------------------------ valid
    def valid(self, parent_id: Optional[int] = None) -> dict:
        return {
            "name": self._name,
            "email": self.email.valid,
            "gender": self._gender,
            "status": self._status,
        }

    # ---------------------------------------------------------------- invalid
    def invalid(
            self,
            parent_id: Optional[int] = None,
            error_type: Union[EmailError, CommonError, List[Enum], None] = None,
    ) -> dict:
        error_type = error_type or EmailError.INVALID
        mapping = {
            EmailError.INVALID: ("email", "invalid_email"),
            EmailError.NONE: ("email", None),
            CommonError.EMPTY: ("name", ""),
        }
        return self.inject_error(self.valid(), error_type, mapping)

    # ------------------------------------------------------------- callable
    def __call__(
            self,
            parent_id: Optional[int] = None,
            *,
            invalid: bool = False,
            error_type: Union[Enum, List[Enum], None] = None,
            **overrides: Any,
    ) -> dict:
        payload = (
            self.invalid(parent_id, error_type) if invalid else self.valid(parent_id)
        )
        payload.update(overrides)
        return payload


class RandomComment(DataGenerator, ErrorInjectionMixin):
    """Factory for comments (belongs to a post)."""

    def __init__(
            self,
            name_variant: FieldVariant | None = None,
            email_variant: FieldVariant | None = None,
            body_variant: FieldVariant | None = None,
    ) -> None:
        self.name = name_variant or FieldVariant(lambda: _FAKER.name())
        self.email = email_variant or FieldVariant(lambda: _FAKER.email())
        self.body = body_variant or FieldVariant(lambda: _FAKER.text(max_nb_chars=200))

    # ------------------------------------------------------------------ valid
    def valid(self, parent_id: Optional[int] = None) -> dict:
        if parent_id is None:
            raise ValueError("Comment requires a post_id (parent_id).")
        return {
            "post_id": parent_id,
            "name": self.name.valid,
            "email": self.email.valid,
            "body": self.body.valid,
        }

    # ---------------------------------------------------------------- invalid
    def invalid(
            self,
            parent_id: Optional[int] = None,
            error_type: Union[Enum, List[Enum], None] = None,
    ) -> dict:
        error_type = error_type or CommonError.EMPTY
        mapping = {
            CommonError.EMPTY: ("name", self.name.empty),
            EmailError.INVALID: ("email", "invalid_email"),
            EmailError.NONE: ("email", None),
            CommonError.NONE: ("body", self.body.none),
        }
        return self.inject_error(self.valid(parent_id), error_type, mapping)

    # ------------------------------------------------------------- callable
    def __call__(
            self,
            parent_id: Optional[int] = None,
            *,
            invalid: bool = False,
            error_type: Union[Enum, List[Enum], None] = None,
            **overrides: Any,
    ) -> dict:
        payload = (
            self.invalid(parent_id, error_type) if invalid else self.valid(parent_id)
        )
        payload.update(overrides)
        return payload
