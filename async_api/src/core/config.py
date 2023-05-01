import os

from pydantic import BaseSettings


class Settings(BaseSettings):
    project_name: str

    redis_host: str
    redis_port: int
    redis_expire_time: int

    elastic_schema: str
    elastic_host: str
    elastic_port: str

    log_level: str

    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

    verify_token_url: str
    secret_key: str
    jwt_algorithm: str
    enable_tracer: bool = True
    enable_before_request: bool = True
    agent_host_name: str = "jaeger"


    class Config:
        env_file = "./.env"
        env_file_encoding = "utf-8"
        case_sensitive = True


settings = Settings()
