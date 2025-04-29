from abc import ABC

from playwright.sync_api import APIRequestContext


class BaseClient(ABC):
    def __init__(self, request_context: APIRequestContext):
        self.context = request_context
