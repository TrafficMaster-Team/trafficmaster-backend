from tests.unit.factories.values import create_answer_option
from trafficmaster.infrastructure.persistence.models.cards import AnswerOptionsType


def test_serializes_and_deserializes_answer_option_entity() -> None:
    option = create_answer_option(text="Answer", rationale="Explanation")
    sut = AnswerOptionsType()

    serialized = sut.process_bind_param([option], dialect=None)
    restored = sut.process_result_value(serialized, dialect=None)

    assert serialized is not None
    assert serialized[0]["id"] == str(option.id)
    assert restored is not None
    assert restored == [option]
    assert restored[0].text == option.text
    assert restored[0].is_correct == option.is_correct
    assert restored[0].rationale == option.rationale
    assert restored[0].created_at == option.created_at
    assert restored[0].updated_at == option.updated_at
