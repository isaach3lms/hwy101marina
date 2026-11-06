import json
import time
from collections import defaultdict, deque

from flask import (
    Blueprint,
    Response,
    current_app,
    redirect,
    render_template,
    request,
    url_for,
)

from . import content, mail
from .forms import ContactForm

bp = Blueprint("site", __name__)

_hits: dict[str, deque] = defaultdict(deque)


def _schema() -> dict:
    s = content.SITE
    base = current_app.config["SITE_URL"]
    return {
        "@context": "https://schema.org",
        "@type": "LocalBusiness",
        "name": s["name"],
        "description": content.PAGES["home"]["description"],
        "url": base + "/",
        "telephone": s["phone_tel"],
        "image": base + url_for("static", filename="img/brand/og-card.jpg"),
        "address": {
            "@type": "PostalAddress",
            "addressLocality": s["locality"],
            "addressRegion": s["region"],
            "addressCountry": s["country"],
        },
        "sameAs": [s["facebook"]],
    }


def render_page(template: str, key: str, **ctx):
    page = content.PAGES[key]
    canonical = current_app.config["SITE_URL"] + page["path"]
    return render_template(template, page=page, canonical=canonical, schema=_schema(), **ctx)


def _rate_limited(ip: str) -> bool:
    now = time.time()
    window = current_app.config["CONTACT_RATE_WINDOW"]
    q = _hits[ip]
    while q and now - q[0] > window:
        q.popleft()
    if len(q) >= current_app.config["CONTACT_RATE_LIMIT"]:
        return True
    q.append(now)
    return False


@bp.get("/")
def home():
    return render_page("home.html", "home", c=content.HOME, photos=content.HOME_PHOTOS)


@bp.get("/rentals/")
def rentals():
    return render_page("rentals.html", "rentals", c=content.RENTALS)


@bp.get("/campground/")
def campground():
    return render_page("campground.html", "campground", c=content.CAMPGROUND)


@bp.get("/store/")
def store():
    return render_page("store.html", "store", c=content.STORE, photos=content.STORE_PHOTOS)


@bp.get("/gallery/")
def gallery():
    return render_page("gallery.html", "gallery", c=content.GALLERY_PAGE, photos=content.GALLERY_PHOTOS)


@bp.route("/contact/", methods=["GET", "POST"])
def contact():
    form = ContactForm()
    error = None
    if form.validate_on_submit():
        if form.website.data:
            # Honeypot tripped: pretend success, send nothing.
            return redirect(url_for("site.contact_thanks"))
        if _rate_limited(request.remote_addr or "unknown"):
            error = "Too many requests from your connection. Please call us instead."
        else:
            labels = dict(content.CONTACT["interests"])
            lead = {
                "name": form.name.data,
                "phone": form.phone.data,
                "interest": form.interest.data,
                "interest_label": labels[form.interest.data],
                "message": form.message.data,
            }
            # Always keep a copy in the service logs so a mail outage never loses a lead.
            current_app.logger.info("contact_lead %s", json.dumps(lead))
            if mail.send_lead(lead):
                return redirect(url_for("site.contact_thanks"))
            if not current_app.config["IS_PRODUCTION"] and not mail.is_configured():
                # Local development without Resend keys: treat as delivered.
                return redirect(url_for("site.contact_thanks"))
            error = content.CONTACT["error_body"]
    return render_page("contact.html", "contact", c=content.CONTACT, form=form, error=error)


@bp.get("/contact/thanks/")
def contact_thanks():
    return render_page("thanks.html", "thanks", c=content.CONTACT)


@bp.get("/healthz")
def healthz():
    return Response("ok", mimetype="text/plain")


@bp.get("/robots.txt")
def robots():
    base = current_app.config["SITE_URL"]
    body = f"User-agent: *\nAllow: /\nDisallow: /contact/thanks/\n\nSitemap: {base}/sitemap.xml\n"
    return Response(body, mimetype="text/plain")


@bp.get("/sitemap.xml")
def sitemap():
    base = current_app.config["SITE_URL"]
    urls = [p["path"] for k, p in content.PAGES.items() if not p.get("noindex")]
    xml = ['<?xml version="1.0" encoding="UTF-8"?>', '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">']
    xml += [f"  <url><loc>{base}{path}</loc></url>" for path in urls]
    xml.append("</urlset>")
    return Response("\n".join(xml) + "\n", mimetype="application/xml")


def _register_legacy_redirects():
    """301 the old WordPress URLs, with or without a trailing slash."""
    for i, (old, new) in enumerate(content.LEGACY_REDIRECTS.items()):
        def view(target=new):
            return redirect(target, code=301)

        # strict_slashes=False on the slashless rule matches both /old and /old/.
        bp.add_url_rule(old, endpoint=f"legacy_{i}", view_func=view, strict_slashes=False)


_register_legacy_redirects()
