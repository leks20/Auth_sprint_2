from app import jwt
from redis_client import redis_client


@jwt.token_in_blocklist_loader
def check_if_token_is_revoked(jwt_header, jwt_payload: dict):
    """
    Callback function to check if a JWT exists in the redis blocklist
    """
    jti = jwt_payload["jti"]
    token_in_redis = redis_client.get(jti)
    return token_in_redis is not None
