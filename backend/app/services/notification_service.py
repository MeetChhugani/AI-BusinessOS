from abc import ABC, abstractmethod
from uuid import UUID
from app.logging.config import logger

class NotificationService(ABC):
    @abstractmethod
    async def send(self, employee_id: UUID, title: str, message: str, category: str) -> None:
        """Sends a system alert/notification to an employee."""
        pass

class DatabaseNotificationService(NotificationService):
    async def send(self, employee_id: UUID, title: str, message: str, category: str) -> None:
        # Logs the notification inside structlog as a database alert record
        logger.info(
            "notification_logged_to_db",
            employee_id=str(employee_id),
            title=title,
            message=message,
            category=category,
        )

class EmailNotificationService(NotificationService):
    async def send(self, employee_id: UUID, title: str, message: str, category: str) -> None:
        # Stub for future SMTP / Resend integrations
        logger.info("notification_sent_email_stub", employee_id=str(employee_id), title=title)

class SlackNotificationService(NotificationService):
    async def send(self, employee_id: UUID, title: str, message: str, category: str) -> None:
        # Stub for future Slack workspace webhooks
        logger.info("notification_sent_slack_stub", employee_id=str(employee_id), title=title)

class TeamsNotificationService(NotificationService):
    async def send(self, employee_id: UUID, title: str, message: str, category: str) -> None:
        # Stub for Microsoft Teams webhooks
        logger.info("notification_sent_teams_stub", employee_id=str(employee_id), title=title)

class PushNotificationService(NotificationService):
    async def send(self, employee_id: UUID, title: str, message: str, category: str) -> None:
        # Stub for WebPush / Firebase notifications
        logger.info("notification_sent_push_stub", employee_id=str(employee_id), title=title)

class AggregateNotificationService(NotificationService):
    """Orchestrator to dispatch alerts across all enabled communication channels."""
    def __init__(self) -> None:
        self.channels = [
            DatabaseNotificationService(),
            EmailNotificationService(),
            SlackNotificationService(),
            TeamsNotificationService(),
            PushNotificationService(),
        ]

    async def send(self, employee_id: UUID, title: str, message: str, category: str) -> None:
        for channel in self.channels:
            try:
                await channel.send(employee_id, title, message, category)
            except Exception as e:
                logger.error(
                    "notification_dispatch_failed",
                    channel=channel.__class__.__name__,
                    employee_id=str(employee_id),
                    error=str(e),
                )

# Unified service instance
notification_service = AggregateNotificationService()
