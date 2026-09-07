from elasticsearch import Elasticsearch

from app.core.config import get_settings


def build_elasticsearch() -> Elasticsearch:
    return Elasticsearch(get_settings().elasticsearch_url, request_timeout=10)


def check_elasticsearch() -> None:
    if not build_elasticsearch().ping():
        raise RuntimeError("elasticsearch ping failed")
