from kafka import KafkaProducer

from app.core.config import get_settings


def build_producer() -> KafkaProducer:
    settings = get_settings()
    kwargs = {
        "bootstrap_servers": settings.kafka_bootstrap_servers.split(","),
        "security_protocol": settings.kafka_security_protocol,
    }
    if settings.kafka_sasl_mechanism:
        kwargs.update(
            sasl_mechanism=settings.kafka_sasl_mechanism,
            sasl_plain_username=settings.kafka_sasl_username,
            sasl_plain_password=settings.kafka_sasl_password,
        )
    return KafkaProducer(**kwargs)


def check_kafka() -> None:
    producer = build_producer()
    producer.bootstrap_connected()
    producer.close()
