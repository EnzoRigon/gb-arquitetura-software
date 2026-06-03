import logging
import smtplib
from email.message import EmailMessage

from sqlalchemy.orm import Session

from app.core.config import settings
from app.models.notification import Notification
from app.models.user import User


logger = logging.getLogger(__name__)


def notify_user(db: Session, user_id: int, message: str) -> Notification:
    notification = Notification(user_id=user_id, message=message)
    db.add(notification)
    db.flush()

    # Simulacao de envio de e-mail/push interno via log.
    user = db.query(User).filter(User.id == user_id).first()
    target = user.email if user else f"user:{user_id}"
    logger.info("Notification to %s: %s", target, message)

    return notification


def send_email(to_email: str, subject: str, body: str) -> bool:
    if not settings.smtp_enabled:
        logger.info("SMTP disabled; skipping email to %s", to_email)
        return False

    message = EmailMessage()
    message["Subject"] = subject
    message["From"] = settings.smtp_sender
    message["To"] = to_email
    message.set_content(body)

    try:
        if settings.smtp_use_ssl:
            with smtplib.SMTP_SSL(settings.smtp_host, settings.smtp_port, timeout=10) as server:
                if settings.smtp_user and settings.smtp_password:
                    server.login(settings.smtp_user, settings.smtp_password)
                server.send_message(message)
        else:
            with smtplib.SMTP(settings.smtp_host, settings.smtp_port, timeout=10) as server:
                if settings.smtp_use_tls:
                    server.starttls()
                if settings.smtp_user and settings.smtp_password:
                    server.login(settings.smtp_user, settings.smtp_password)
                server.send_message(message)

        logger.info("Email sent to %s", to_email)
        return True
    except Exception as exc:
        logger.warning("Failed to send email to %s: %s", to_email, exc)
        return False


def send_task_created_email(to_email: str, task_title: str) -> bool:
    subject = "Nova tarefa criada"
    body = f"Uma nova tarefa foi criada para voce: {task_title}"
    return send_email(to_email=to_email, subject=subject, body=body)
