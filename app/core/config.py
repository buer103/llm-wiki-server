from functools import lru_cache

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str = "llm-wiki-server"
    app_env: str = "dev"
    app_host: str = "0.0.0.0"
    app_port: int = 8080
    log_level: str = "INFO"
    api_prefix: str = "/v1/llm-wiki-server"

    mysql_dsn: str = "mysql+pymysql://llm_wiki:llm_wiki@localhost:3306/llm_wiki"
    mysql_pool_size: int = Field(default=5, ge=1, le=50)
    mysql_max_overflow: int = Field(default=10, ge=0, le=100)
    redis_url: str = "redis://localhost:6379/0"
    elasticsearch_url: str = "http://localhost:9200"
    kafka_bootstrap_servers: str = "localhost:9092"
    kafka_security_protocol: str = "PLAINTEXT"
    kafka_sasl_mechanism: str = ""
    kafka_sasl_username: str = ""
    kafka_sasl_password: str = ""
    obs_endpoint: str = ""
    obs_bucket: str = ""
    obs_access_key: str = ""
    obs_secret_key: str = ""
    litellm_base_url: str = ""
    litellm_api_key: str = ""
    viam_base_url: str = ""
    viam_timeout_seconds: float = Field(default=5.0, gt=0, le=60)
    infrastructure_check_timeout_seconds: float = Field(default=3.0, gt=0, le=30)

    model_config = SettingsConfigDict(env_file=".env", env_prefix="LLM_WIKI_", extra="ignore")


@lru_cache
def get_settings() -> Settings:
    return Settings()
