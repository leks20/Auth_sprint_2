from pathlib import Path

from pydantic import BaseSettings, Field


class TestSettings(BaseSettings):
    elastic_schema: str = Field("http", env="elastic_schema")
    elastic_host: str = Field("127.0.0.1", env="elastic_host")
    elastic_port: str = Field("9200", env="elastic_port")
    redis_host: str = Field("127.0.0.1", env="redis_host")
    redis_port: str = Field("6379", env="redis_port")
    service_schema: str = Field("http", env="service_schema")
    service_url: str = Field("127.0.0.1", env="service_url")
    service_port: str = Field("8000", env="service_port")

    schemes_dir: Path = Field(Path(__file__).parent.joinpath("testdata/schemes"))
    data_dir: Path = Field(Path(__file__).parent.joinpath("testdata/data"))

    class Config:
        env_file = ".env"


config: TestSettings = TestSettings()
