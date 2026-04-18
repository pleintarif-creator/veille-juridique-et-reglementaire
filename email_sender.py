"""Envoi de la newsletter par SMTP."""

from __future__ import annotations

import logging
import os
import smtplib
import ssl
from email.message import EmailMessage

logger = logging.getLogger(__name__)


class EmailConfigError(RuntimeError):
    pass


def _env(name: str, required: bool = True, default: str | None = None) -> str:
    value = os.environ.get(name, default)
    if required and not value:
        raise EmailConfigError(
            f"Variable d'environnement manquante : {name}. "
            "Configurez-la via les GitHub Secrets."
        )
    return value or ""


def send(subject: str, html_body: str, text_body: str) -> None:
    host = _env("SMTP_HOST")
    port = int(_env("SMTP_PORT", default="587"))
    user = _env("SMTP_USER")
    password = _env("SMTP_PASSWORD")
    sender = _env("EMAIL_FROM", required=False) or user
    to_raw = _env("EMAIL_TO")
    recipients = [r.strip() for r in to_raw.split(",") if r.strip()]
    if not recipients:
        raise EmailConfigError("EMAIL_TO ne contient aucun destinataire.")

    msg = EmailMessage()
    msg["Subject"] = subject
    msg["From"] = sender
    msg["To"] = ", ".join(recipients)
    msg.set_content(text_body)
    msg.add_alternative(html_body, subtype="html")

    context = ssl.create_default_context()

    logger.info("Envoi SMTP via %s:%s à %s", host, port, recipients)
    if port == 465:
        with smtplib.SMTP_SSL(host, port, context=context, timeout=30) as srv:
            srv.login(user, password)
            srv.send_message(msg)
    else:
        with smtplib.SMTP(host, port, timeout=30) as srv:
            srv.ehlo()
            srv.starttls(context=context)
            srv.ehlo()
            srv.login(user, password)
            srv.send_message(msg)
    logger.info("Email envoyé avec succès.")
