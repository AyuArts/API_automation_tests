import json
import pathlib
from functools import lru_cache

import allure

_JSON_PATH = pathlib.Path(__file__).with_name("friendly_titles.json")


@lru_cache(maxsize=1)
def _load_titles() -> dict:
    with _JSON_PATH.open(encoding="utf-8") as fh:
        return json.load(fh)


def auto_allure(module_key: str):
    """
    Returns the decorator-class that will put down to each test_* method
    Title / Story / Severity from Friendly_titles.json on the key module_key.
    """

    titles = _load_titles().get(module_key, {})

    def _decorate(cls):
        for name, attr in cls.__dict__.items():
            if not callable(attr) or not name.startswith("test_"):
                continue
            if name not in titles:
                continue

            meta = titles[name]
            attr = allure.title(meta["title"])(attr)
            attr = allure.story(meta["story"])(attr)

            sev = meta.get("severity")
            if sev:
                attr = allure.severity(getattr(allure.severity_level, sev))(attr)

            setattr(cls, name, attr)
        return cls

    return _decorate
