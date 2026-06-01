from unittest.mock import Mock

from trafficmaster.application.auth.log_out import LogOutHandler


async def test_logs_out_successfully(fake_auth_session_service: Mock) -> None:
    # Arrange
    handler = LogOutHandler(auth_service=fake_auth_session_service)

    # Act
    await handler()

    # Assert
    fake_auth_session_service.invalidate_current_session.assert_awaited_once()
