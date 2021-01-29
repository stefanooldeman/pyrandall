import os
import pytest
from freezegun import freeze_time

from pyrandall.kafka import KafkaConn
from pyrandall.kafka import KafkaTopicError 

from confluent_kafka.admin import AdminClient
from confluent_kafka import KafkaError
from confluent_kafka.cimpl import KafkaException


def ensure_topics_do_not_exist(topics: [str]):
    admin = AdminClient({ 'bootstrap.servers': 'localhost:9092' })
    futures = admin.delete_topics(topics)
    for topic,future in futures.items():
        try:
            future.result()
        except KafkaException as e:
            # unwrap to KafkaError
            error = e.args[0]
            if error.code() == KafkaError.UNKNOWN_TOPIC_OR_PART:
                # topic not present, safely ignore
                pass
            else:
                raise e
        assert future.done()


def test_validate_topic_not_found(kafka_cluster_info):
    ensure_topics_do_not_exist(['fdsjkfldsfjdksl'])

    with pytest.raises(KafkaTopicError) as e:
        kafka = KafkaConn()
        kafka.consume("fdsjkfldsfjdksl", topic_timeout=2.0)

    assert "Topic fdsjkfldsfjdksl does not exist" in e.value.message
