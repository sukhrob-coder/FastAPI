from fastcrud import FastCRUD

from .models import RateLimit
from .schemas import (
    RateLimitCreateInternal,
    RateLimitDelete,
    RateLimitRead,
    RateLimitUpdate,
    RateLimitUpdateInternal,
)

CRUDRateLimit = FastCRUD[
    RateLimit, RateLimitCreateInternal, RateLimitUpdate, RateLimitUpdateInternal, RateLimitDelete, RateLimitRead
]
crud_rate_limits = CRUDRateLimit(RateLimit)
