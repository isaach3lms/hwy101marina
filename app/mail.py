"""Contact form delivery through the Resend HTTP API (port 443, not SMTP)."""
import logging

import requests
from flask import current_app

RESEND_URL = "https://api.resend.com/emails"
log = logging.getLogger(__name__)


def is_configured() -> bool:
    return bool(current_app.config.get("MAIL_CONFIGURED"))


def _clean(value: str, limit: int) -> str:
    return " ".join((value or "").split())[:limit]


def send_lead(lead: dict) -> bool:
    """Email a contact form lead to the marina. Returns True on success."""
    if not is_configured():
        return False

    interest = _clean(lead["interest_label"], 40)
    subject = f"New {interest.lower()} inquiry from {_clean(lead['name'], 60)}"
    body = (
        f"Name: {_clean(lead['name'], 100)}\n"
        f"Phone: {_clean(lead['phone'], 30)}\n"
        + (f"Email: {_clean(lead['email'], 120)}\n" if lead.get("email") else "")
        + f"Interested in: {interest}\n\n"
        f"Question:\n{lead['message'].strip()}\n"
    )
    payload = {
        "from": current_app.config["MAIL_FROM"],
        "to": current_app.config["MAIL_TO"],
        "subject": subject,
        "text": body,
    }
    try:
        resp = requests.post(
            RESEND_URL,
            headers={"Authorization": f"Bearer {current_app.config['RESEND_API_KEY']}"},
            json=payload,
            timeout=10,
        )
    except requests.RequestException:
        log.exception("Resend request failed")
        return False
    if resp.status_code >= 300:
        log.error("Resend returned %s: %s", resp.status_code, resp.text[:300])
        return False
    return True
