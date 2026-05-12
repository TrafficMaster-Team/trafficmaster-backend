import uuid
from typing import override

from trafficmaster.domain.card_progress.ports.review_id_generator import ReviewIDGenerator
from trafficmaster.domain.card_progress.values.review_log_id import ReviewLogID


class UUID4ReviewIdGenerator(ReviewIDGenerator):
    @override
    def __call__(self) -> ReviewLogID:
        return ReviewLogID(uuid.uuid4())
