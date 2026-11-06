"""Runtime configuration, read from the environment.

Production hard-fails at boot when required settings are missing, so a
misconfigured deploy never serves traffic with an insecure default.
"""
import os


class ConfigError(RuntimeError):
    pass


def load_config() -> dict:
    env = os.environ.get("APP_ENV", "development").lower()
    is_prod = env == "production"

    secret = os.environ.get("SECRET_KEY")
    if is_prod and not secret:
        raise ConfigError("SECRET_KEY must be set when APP_ENV=production")

    cfg = {
        "APP_ENV": env,
        "IS_PRODUCTION": is_prod,
        "SECRET_KEY": secret or "dev-only-not-for-production",
        "SITE_URL": os.environ.get("SITE_URL", "https://www.hwy101marina.com").rstrip("/"),
        # Resend HTTP API (port 443). Used by the contact form.
        "RESEND_API_KEY": os.environ.get("RESEND_API_KEY", ""),
        "MAIL_FROM": os.environ.get("MAIL_FROM", ""),
        "MAIL_TO": [a.strip() for a in os.environ.get("MAIL_TO", "").split(",") if a.strip()],
        # Forms
        "WTF_CSRF_TIME_LIMIT": 60 * 60 * 8,
        "CONTACT_RATE_LIMIT": int(os.environ.get("CONTACT_RATE_LIMIT", "5")),
        "CONTACT_RATE_WINDOW": int(os.environ.get("CONTACT_RATE_WINDOW", str(60 * 60))),
        # Static assets are not fingerprinted by the build, the app adds ?v=mtime.
        "SEND_FILE_MAX_AGE_DEFAULT": 60 * 60 * 24 * 30,
        "SESSION_COOKIE_SECURE": is_prod,
        "SESSION_COOKIE_HTTPONLY": True,
        "SESSION_COOKIE_SAMESITE": "Lax",
    }

    if is_prod and not (cfg["RESEND_API_KEY"] and cfg["MAIL_FROM"] and cfg["MAIL_TO"]):
        # Not fatal: the site still works and every lead is written to the logs,
        # but the contact form will tell visitors to call instead of promising a callback.
        cfg["MAIL_CONFIGURED"] = False
    else:
        cfg["MAIL_CONFIGURED"] = bool(cfg["RESEND_API_KEY"] and cfg["MAIL_FROM"] and cfg["MAIL_TO"])

    return cfg
