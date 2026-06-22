"""
Email sending helpers. In development (no SMTP creds configured) emails
are logged to the console instead of sent, so the auth flow is testable
without an SMTP server.
"""
import logging

from app.core.config import settings

logger = logging.getLogger(__name__)


def _send_or_log(to_email: str, subject: str, body: str) -> None:
    if not settings.SMTP_USER or not settings.SMTP_PASSWORD:
        logger.info("[DEV EMAIL] To: %s | Subject: %s\n%s", to_email, subject, body)
        return

    import smtplib
    from email.mime.text import MIMEText

    msg = MIMEText(body, "html")
    msg["Subject"] = subject
    msg["From"] = settings.EMAILS_FROM_EMAIL
    msg["To"] = to_email

    with smtplib.SMTP(settings.SMTP_HOST, settings.SMTP_PORT) as server:
        server.starttls()
        server.login(settings.SMTP_USER, settings.SMTP_PASSWORD)
        server.send_message(msg)


def send_verification_email(to_email: str, token: str) -> None:
    link = f"{settings.FRONTEND_URL}/verify-email?token={token}"
    _send_or_log(
        to_email,
        "Verify your InsightFlow AI account",
        f"<p>Welcome to InsightFlow AI! Click <a href='{link}'>here</a> to verify your email.</p>",
    )


def send_password_reset_email(to_email: str, token: str) -> None:
    link = f"{settings.FRONTEND_URL}/reset-password?token={token}"
    _send_or_log(
        to_email,
        "Reset your InsightFlow AI password",
        f"<p>Click <a href='{link}'>here</a> to reset your password. This link expires in 30 minutes.</p>",
    )
