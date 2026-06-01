from trafficmaster.domain.card_progress.values.card_state import CardState


def test_card_state_members() -> None:
    assert CardState.NEW == "new"
    assert CardState.LEARNING == "learning"
    assert CardState.REVIEW == "review"
    assert CardState.RELEARNING == "relearning"


def test_card_state_can_be_built_from_value() -> None:
    assert CardState("new") is CardState.NEW
    assert CardState("relearning") is CardState.RELEARNING
