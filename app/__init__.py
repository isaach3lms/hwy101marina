import os
from datetime import datetime, timezone

from flask import Flask, render_template, request, url_for
from flask_wtf.csrf import CSRFError, CSRFProtect
from werkzeug.middleware.proxy_fix import ProxyFix

from config import load_config

from . import brand, content

csrf = CSRFProtect()


def create_app(overrides: dict | None = None) -> Flask:
    app = Flask(__name__)
    app.config.update(load_config())
    if overrides:
        app.config.update(overrides)
        # Keep derived flag in sync when tests override mail settings.
        app.config["MAIL_CONFIGURED"] = overrides.get(
            "MAIL_CONFIGURED",
            bool(app.config["RESEND_API_KEY"] and app.config["MAIL_FROM"] and app.config["MAIL_TO"]),
        )

    # Render terminates TLS in front of gunicorn.
    app.wsgi_app = ProxyFix(app.wsgi_app, x_for=1, x_proto=1, x_host=1)
    csrf.init_app(app)

    from .routes import bp

    app.register_blueprint(bp)

    @app.context_processor
    def inject_globals():
        def asset(path: str) -> str:
            """url_for('static') with ?v=mtime so deploys bust the browser cache."""
            full = os.path.join(app.static_folder, path)
            try:
                version = int(os.path.getmtime(full))
            except OSError:
                version = 0
            return url_for("static", filename=path, v=version)

        return {
            "site": content.SITE,
            "nav": content.NAV,
            "brand": brand.BRAND,
            "brand_css": brand.css_tokens(),
            "asset": asset,
            "year": datetime.now(timezone.utc).year,
            "site_url": app.config["SITE_URL"],
            "web3forms_key": app.config["WEB3FORMS_ACCESS_KEY"],
        }

    @app.after_request
    def security_headers(resp):
        resp.headers.setdefault("X-Content-Type-Options", "nosniff")
        resp.headers.setdefault("X-Frame-Options", "DENY")
        resp.headers.setdefault("Referrer-Policy", "strict-origin-when-cross-origin")
        resp.headers.setdefault("Permissions-Policy", "camera=(), microphone=(), geolocation=()")
        connect = "'self'"
        if app.config["WEB3FORMS_ACCESS_KEY"]:
            connect += " https://api.web3forms.com"
        resp.headers.setdefault(
            "Content-Security-Policy",
            "default-src 'self'; img-src 'self' data:; "
            "style-src 'self' 'unsafe-inline' https://fonts.googleapis.com; "
            f"font-src https://fonts.gstatic.com; script-src 'self'; connect-src {connect}; "
            "form-action 'self'; frame-ancestors 'none'; base-uri 'self'",
        )
        if app.config["IS_PRODUCTION"]:
            resp.headers.setdefault("Strict-Transport-Security", "max-age=31536000")
        return resp

    @app.errorhandler(CSRFError)
    def csrf_failed(_e):
        # An expired or missing form token: show the form again with a plain message.
        from .forms import ContactForm
        from .routes import render_page

        return (
            render_page(
                "contact.html",
                "contact",
                c=content.CONTACT,
                form=ContactForm(),
                error="Your form timed out. Please send it again, or call us.",
            ),
            400,
        )

    @app.errorhandler(404)
    def not_found(_e):
        page = content.PAGES["not_found"]
        return (
            render_template(
                "404.html",
                page=page,
                canonical=app.config["SITE_URL"] + request.path,
            ),
            404,
        )

    @app.errorhandler(500)
    def server_error(_e):
        # Standalone template: no base.html, no DB, no url_for, nothing that can fail again.
        return render_template("errors/500.html", phone=content.SITE), 500

    return app
