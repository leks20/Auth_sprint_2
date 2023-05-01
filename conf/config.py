from typing import Any, Dict

from pydantic import BaseSettings, PostgresDsn, validator


class Settings(BaseSettings):
    secret_key: str
    jwt_algorithm: str

    postgres_host: str
    postgres_password: str
    postgres_user: str
    postgres_db: str
    postgres_port: int

    redis_host: str
    redis_port: int

    service_host: str
    service_port: int
    service_protocol: str
    service_workers: int

    access_expires: int
    refresh_expires: int

    sqlalchemy_database_uri: PostgresDsn | None = None

    request_limit_per_minute: int
    enable_before_request: bool = False
    enable_tracer: bool = True
    agent_host_name: str = "jaeger"

    @validator("sqlalchemy_database_uri", pre=True)
    def assemble_db_connection(cls, v: str | None, values: Dict[str, Any]) -> Any:
        if isinstance(v, str):
            return v

        return PostgresDsn.build(
            scheme="postgresql",
            user=values.get("postgres_user"),
            password=values.get("postgres_password"),
            host=values.get("postgres_host"),
            path=f"/{values.get('postgres_db') or ''}",
            port=str(values.get("postgres_port")),
        )

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = True


settings = Settings()
