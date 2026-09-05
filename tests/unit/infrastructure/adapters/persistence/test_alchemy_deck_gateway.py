from unittest.mock import AsyncMock, Mock, patch

from sqlalchemy.ext.asyncio import AsyncSession

from trafficmaster.application.common.query_params.pagination import Pagination
from trafficmaster.infrastructure.adapters.persistence.alchemy_deck_gateway import AlchemyDeckGateway
from trafficmaster.infrastructure.persistence.models.decks import decks_table


async def test_read_public_decks_filters_private_decks_and_applies_pagination() -> None:
    session = Mock(spec=AsyncSession)
    session.execute = AsyncMock()
    rows = Mock()
    rows.scalars.return_value.all.return_value = []
    session.execute.return_value = rows
    statement = Mock()
    statement.where.return_value = statement
    statement.offset.return_value = statement
    statement.limit.return_value = statement

    with patch(
        "trafficmaster.infrastructure.adapters.persistence.alchemy_deck_gateway.select",
        return_value=statement,
    ):
        gateway = AlchemyDeckGateway(session)
        result = await gateway.read_public_decks(Pagination(limit=20, offset=40))

    assert result == []
    condition = statement.where.call_args.args[0]
    assert condition.compare(decks_table.c.is_public.is_(True))
    statement.offset.assert_called_once_with(40)
    statement.limit.assert_called_once_with(20)
    session.execute.assert_awaited_once_with(statement)
