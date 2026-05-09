from dataclasses import dataclass


@dataclass(frozen=True, slots=True, kw_only=True)
class UserAggregateStatsView:
    total_decks: int
    total_cards: int
    new_count: int
    learning_count: int
    review_count: int
    due_learning: int
    due_review: int
    new_done_today: int
    reviews_done_today: int
