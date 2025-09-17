import json
from typing import Optional

from fastapi import Query


class CommonParams:
    def __init__(
        self,
        filter: Optional[str] = Query(default=None),
        sort: Optional[str] = Query(default=None),
        search: str = Query(default=""),
        group_by: Optional[str] = Query(default=None),
        limit: int = Query(default=100, ge=1),
        offset: int = Query(default=0, ge=0),
    ):
        if filter:
            try:
                self.filter = json.loads(filter)
            except Exception:
                self.filter = filter
        else:
            self.filter = []

        if sort:
            try:
                self.sort = json.loads(sort)
            except Exception:
                self.sort = sort
        else:
            self.sort = []

        self.search = search
        self.group_by = group_by
        self.limit = limit
        self.offset = offset
