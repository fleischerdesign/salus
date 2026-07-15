import logging
from salus.exceptions import NotFoundError
from salus.models.notification import Notification
from salus.repositories.unit_of_work import IUnitOfWork

logger = logging.getLogger("salus.services.notification")


class NotificationService:
    def __init__(self, uow: IUnitOfWork) -> None:
        self.uow = uow

    def create_notification(
        self, user_id: str, title: str, message: str, category: str = "system"
    ) -> Notification:
        with self.uow:
            # Check user exists
            user = self.uow.users.get_by_id(user_id)
            if not user:
                raise NotFoundError("User not found")

            notif = Notification(
                user_id=user_id,
                title=title,
                message=message,
                category=category,
            )
            self.uow.notifications.create(notif)
            logger.info(f"Created notification '{title}' for user {user_id}")
            return notif

    def get_unread(self, user_id: str) -> list[Notification]:
        with self.uow:
            return self.uow.notifications.find_unread_by_user(user_id)

    def get_all(self, user_id: str, limit: int = 20) -> list[Notification]:
        with self.uow:
            return self.uow.notifications.find_by_user(user_id, limit=limit)

    def mark_as_read(self, user_id: str, notification_id: str) -> Notification:
        with self.uow:
            notif = self.uow.notifications.get_by_id(notification_id)
            if not notif or notif.user_id != user_id:
                raise NotFoundError("Notification not found")

            notif.is_read = True
            self.uow.notifications.update(notif)
            return notif

    def mark_all_as_read(self, user_id: str) -> None:
        with self.uow:
            self.uow.notifications.mark_all_read(user_id)
