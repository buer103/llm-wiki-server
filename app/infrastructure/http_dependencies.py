import httpx

from app.core.config import get_settings


def check_http_endpoint(base_url: str, path: str = "/") -> None:
    if not base_url:
        raise RuntimeError("endpoint is not configured")
    url = f"{base_url.rstrip('/')}/{path.lstrip('/')}"
    response = httpx.get(url, timeout=get_settings().infrastructure_check_timeout_seconds)
    response.raise_for_status()


def check_litellm() -> None:
    check_http_endpoint(get_settings().litellm_base_url, "/health")


def check_viam() -> None:
    check_http_endpoint(get_settings().viam_base_url, "/health")


def check_obs() -> None:
    check_http_endpoint(get_settings().obs_endpoint, "/")
