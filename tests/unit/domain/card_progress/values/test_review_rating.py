from trafficmaster.domain.card_progress.values.review_rating import ReviewRating


def test_review_rating_values() -> None:
    assert ReviewRating.AGAIN == 1
    assert ReviewRating.HARD == 2
    assert ReviewRating.GOOD == 3
    assert ReviewRating.EASY == 4


def test_review_rating_ordering() -> None:
    assert ReviewRating.AGAIN < ReviewRating.HARD < ReviewRating.GOOD < ReviewRating.EASY
