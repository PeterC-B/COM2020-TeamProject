
from dataclasses import dataclass
from typing import Any


@dataclass(frozen=True)
class ListUsersResult:
    items: list[Any]
    total: int

class ListUsers:
    def __init__(self, user_repo):
        self.user_repo = user_repo

    def execute(self) -> ListUsersResult:

        users, total = self.user_repo.get()


        return ListUsersResult(items=users, total=total)
