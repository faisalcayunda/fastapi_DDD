from typing import Dict, List, Optional, Union, override

from pydantic import BaseModel


class BaseResponse(BaseModel):
    """Base response model."""

    code: str
    data: Optional[Dict] = None


class ListResponse(BaseResponse):
    """List response model."""

    data: List
    meta: Optional[Union[Dict, List]] = None


class ErrorResponse(BaseModel):
    """Error response model."""

    code: str
    error: Optional[Union[Dict, List]]  # dynamic error message
