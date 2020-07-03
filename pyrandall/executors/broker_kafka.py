from pyrandall.kafka import KafkaConn
from pyrandall.types import Assertion, ExecutionMode, UnorderedDiffAssertion
from .common import Executor


class BrokerKafka(Executor):
    def __init__(self, spec, *args, **kwargs):
        super().__init__(spec)

    def execute(self):
        if self.execution_mode is ExecutionMode.SIMULATING:
            return self.simulate(self.spec)
        elif self.execution_mode is ExecutionMode.VALIDATING:
            return self.validate(self.spec)

    def simulate(self, spec):
        kafka = KafkaConn()
        kafka.init_producer()

        with Assertion(
            "events_produced", spec.assertions, "produced a event"
        ) as a:
            send = 0
            for event in spec.events:
                kafka.produce_message(spec.topic, event)
                send += 1
            a.actual_value = send
            yield a

    def validate(self, spec):
        kafka = KafkaConn()
        kafka.check_connection()
        consumed = kafka.consume(spec.topic, spec.assertions.get("timeout_after", 2.0))
        with Assertion(
            "total_events", spec.assertions, "total amount of received events"
        ) as a:
            a.actual_value = len(consumed)
            yield a

        with UnorderedDiffAssertion(
            "unordered", spec.assertions, "unordered events"
        ) as a:
            a.actual_value = consumed
            yield a

    def represent(self):
        return (
            f"BrokerKafka {self.spec.execution_mode.represent()} to {self.spec.topic}"
        )
