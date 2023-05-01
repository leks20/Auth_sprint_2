from flask_limiter import Limiter
from flask_jwt_extended import get_jwt_identity
from auth_app.app import app
from conf.config import settings


limiter = Limiter(
    app=app,
    key_func=lambda: get_jwt_identity()["id"],
    storage_uri=f"redis://{settings.redis_host}:{settings.redis_port}",
    default_limits=[f"{settings.request_limit_per_minute} per minute"]
)