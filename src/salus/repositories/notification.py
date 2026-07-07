from sqlmodel import select, desc

from salus.models.notification import Notification
from salus.repositories.base import Repository
from salus.repositories.protocols import INotificationRepository


class NotificationRepository(Repository[Notification], INotificationRepository):
    model = Notification

    def find_by_user(self, user_id: int, limit: int = 20) -> list[Notification]:
        return list(
            self.session.exec(
                select(Notification)
                .where(Notification.user_id == user_id)
                .order_by(desc(Notification.created_at))
                .limit(limit)
            ).all()
        )

    def find_unread_by_user(self, user_id: int) -> list[Notification]:
        return list(
            self.session.exec(
                select(Notification)
                .where(Notification.user_id == user_id, Notification.is_read == False)  # type: ignore # noqa: E712
                .order_by(desc(Notification.created_at))
            ).all()
        )

    def mark_all_read(self, user_id: int) -> None:
        unread = self.find_unread_by_user(user_id)
        for notif in unread:
            notif.is_read = True
            self.update(notif)
