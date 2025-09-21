from typing import Any, override

from fastapi.responses import JSONResponse

from app.utils.helpers import orjson_dumps


class ORJSONResponse(JSONResponse):
    """Custom JSONResponse menggunakan orjson."""

    media_type = "application/json"

    @override
    def render(self, content: Any) -> bytes:
        """Render content menggunakan orjson."""
        return orjson_dumps(content)
