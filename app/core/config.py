from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str = "llm-wiki-server"
    app_env: str = "dev"
    app_host: str = "0.0.0.0"
    app_port: int = 8080
    log_level: str = "INFO"
    api_prefix: str = "/v1/llm-wiki-server"

    mysql_dsn: str = "mysql+pymysql://llm_wiki:llm_wiki@localhost:3306/llm_wiki"
    redis_url: str = "redis://localhost:6379/0"
    elasticsearch_url: str = "http://localhost:9200"
    kafka_bootstrap_servers: str = "localhost:9092"
    obs_endpoint: str = ""
    obs_bucket: str = ""
    litellm_base_url: str = ""
    viam_base_url: str = ""

    model_config = SettingsConfigDict(env_file=".env", env_prefix="LLM_WIKI_", extra="ignore")


@lru_cache
def get_settings() -> Settings:
    return Settings()
