import re
from pathlib import Path
from unittest.mock import patch

import pytest

from app import content, create_app
from config import ConfigError

ROOT = Path(__file__).resolve().parent.parent
PAGES = ["/", "/rentals/", "/campground/", "/store/", "/gallery/", "/contact/"]


@pytest.mark.parametrize("path", PAGES)
def test_pages_render_with_seo(client, path):
    r = client.get(path)
    assert r.status_code == 200
    html = r.get_data(as_text=True)
    assert "<title>" in html and 'rel="canonical"' in html
    assert f'href="https://www.hwy101marina.com{path}"' in html
    assert "tel:+18704675252" in html


def test_home_copy_and_schema(client):
    html = client.get("/").get_data(as_text=True)
    assert "get your feet wet" in html.lower()
    assert '"@type": "LocalBusiness"' in html
    assert "(870) 467-5252" in html


def test_rental_prices_match_live_site(client):
    html = client.get("/rentals/").get_data(as_text=True)
    prices = sorted(b["price"] for b in content.RENTALS["boats"])
    assert prices == [285, 285, 295, 375, 485, 485, 575]
    for p in set(prices):
        assert f"${p}" in html
    assert html.count("per day + tax") == 7


def test_campground_price(client):
    html = client.get("/campground/").get_data(as_text=True)
    assert "$20.00" in html and "14 campsites" in html


@pytest.mark.parametrize("old,new", list(content.LEGACY_REDIRECTS.items()))
def test_legacy_wordpress_urls_redirect(client, old, new):
    for variant in {old, old + "/"} if not old.endswith(".xml") else {old}:
        r = client.get(variant)
        assert r.status_code == 301, variant
        assert r.headers["Location"].endswith(new)


def test_404_renders_branded_page(client):
    r = client.get("/nope")
    assert r.status_code == 404
    assert "We could not find that page" in r.get_data(as_text=True)


def test_500_page_is_standalone(app):
    @app.get("/boom")
    def boom():
        raise RuntimeError("x")

    app.config["PROPAGATE_EXCEPTIONS"] = False
    app.config["TESTING"] = False
    r = app.test_client().get("/boom")
    assert r.status_code == 500
    html = r.get_data(as_text=True)
    assert "tel:+18704675252" in html
    assert "site.css" not in html  # decoupled from base.html


def test_500_template_does_not_extend_base():
    src = (ROOT / "app/templates/errors/500.html").read_text()
    assert "extends" not in src and "url_for" not in src


def test_health_robots_sitemap(client):
    assert client.get("/healthz").data == b"ok"
    robots = client.get("/robots.txt").get_data(as_text=True)
    assert "Sitemap: https://www.hwy101marina.com/sitemap.xml" in robots
    sm = client.get("/sitemap.xml").get_data(as_text=True)
    for path in PAGES:
        assert f"https://www.hwy101marina.com{path}</loc>" in sm
    assert "/contact/thanks/" not in sm


def test_security_headers(client):
    h = client.get("/").headers
    assert h["X-Content-Type-Options"] == "nosniff"
    assert "frame-ancestors 'none'" in h["Content-Security-Policy"]


def test_all_referenced_images_exist(client):
    static = ROOT / "app/static"
    for p in content.GALLERY_PHOTOS + content.STORE_PHOTOS + content.HOME_PHOTOS:
        assert (static / p["full"]).exists(), p["full"]
        assert (static / p["thumb"]).exists(), p["thumb"]
    for b in content.RENTALS["boats"]:
        assert (static / "img/boats" / b["image"]).exists()
    icons = [t["icon"] for t in content.HOME["tiles"]]
    icons += [s["icon"] for s in content.RENTALS["strip"]] + [f["icon"] for f in content.CAMPGROUND["features"]]
    for i in icons:
        assert (static / "img/icons" / i).exists(), i


def test_every_rendered_image_resolves(client):
    for path in PAGES:
        html = client.get(path).get_data(as_text=True)
        for src in re.findall(r'src="(/static/[^"?]+)', html):
            assert client.get(src).status_code == 200, src


def test_no_em_dashes_anywhere():
    bad = chr(0x2014)
    for f in list((ROOT / "app").rglob("*.py")) + list((ROOT / "app/templates").rglob("*.html")) \
            + list((ROOT / "app/static").rglob("*.css")) + list((ROOT / "app/static").rglob("*.js")):
        assert bad not in f.read_text(), f
    for f in (ROOT / "README.md", ROOT / "render.yaml"):
        assert bad not in f.read_text(), f


def test_brand_tokens_are_only_theming_lever(client):
    html = client.get("/").get_data(as_text=True)
    assert "--orange: #FF5003" in html and "--indigo: #1E0ECC" in html
    css = (ROOT / "app/static/css/site.css").read_text()
    # Brand hexes belong in brand.py; the stylesheet should consume variables.
    assert "#FF5003" not in css.upper() and "#1E0ECC" not in css.upper()


# ---- contact form ----------------------------------------------------------

GOOD = {"name": "Pat Smith", "phone": "(870) 555-0100", "interest": "boating", "message": "Is the 24' pontoon open Saturday?"}


def test_contact_validation_errors(client):
    r = client.post("/contact/", data={"name": "", "phone": "123", "interest": "boating", "message": ""})
    assert r.status_code == 200
    html = r.get_data(as_text=True)
    assert html.count('class="field-error"') >= 3


def test_contact_rejects_bad_interest(client):
    r = client.post("/contact/", data={**GOOD, "interest": "yacht"})
    assert r.status_code == 200 and "field-error" in r.get_data(as_text=True)


def test_contact_dev_success_without_mail_keys(client):
    r = client.post("/contact/", data=GOOD)
    assert r.status_code == 302 and r.headers["Location"].endswith("/contact/thanks/")


def test_contact_sends_via_resend():
    app = create_app({"TESTING": True, "SECRET_KEY": "t", "WTF_CSRF_ENABLED": False,
                      "RESEND_API_KEY": "re_test", "MAIL_FROM": "Marina <noreply@example.com>", "MAIL_TO": ["boss@example.com"]})
    with patch("app.mail.requests.post") as post:
        post.return_value.status_code = 200
        r = app.test_client().post("/contact/", data=GOOD)
    assert r.status_code == 302
    kwargs = post.call_args.kwargs
    assert kwargs["headers"]["Authorization"] == "Bearer re_test"
    assert kwargs["json"]["to"] == ["boss@example.com"]
    assert "Pat Smith" in kwargs["json"]["subject"]
    assert "boating rental" in kwargs["json"]["subject"]
    assert "(870) 555-0100" in kwargs["json"]["text"]


def test_contact_mail_failure_tells_visitor_to_call():
    app = create_app({"TESTING": True, "SECRET_KEY": "t", "WTF_CSRF_ENABLED": False, "IS_PRODUCTION": True,
                      "RESEND_API_KEY": "re_test", "MAIL_FROM": "a@b.co", "MAIL_TO": ["x@y.co"]})
    with patch("app.mail.requests.post") as post:
        post.return_value.status_code = 500
        post.return_value.text = "err"
        r = app.test_client().post("/contact/", data=GOOD)
    assert r.status_code == 200
    assert "call us directly" in r.get_data(as_text=True).lower()


def test_contact_honeypot_sends_nothing():
    app = create_app({"TESTING": True, "SECRET_KEY": "t", "WTF_CSRF_ENABLED": False,
                      "RESEND_API_KEY": "re_test", "MAIL_FROM": "a@b.co", "MAIL_TO": ["x@y.co"]})
    with patch("app.mail.requests.post") as post:
        r = app.test_client().post("/contact/", data={**GOOD, "website": "http://spam.example"})
    assert r.status_code == 302
    post.assert_not_called()


def test_contact_rate_limit():
    app = create_app({"TESTING": True, "SECRET_KEY": "t", "WTF_CSRF_ENABLED": False, "CONTACT_RATE_LIMIT": 2})
    from app import routes
    routes._hits.clear()
    c = app.test_client()
    assert c.post("/contact/", data=GOOD).status_code == 302
    assert c.post("/contact/", data=GOOD).status_code == 302
    r = c.post("/contact/", data=GOOD)
    assert r.status_code == 200 and "Too many requests" in r.get_data(as_text=True)


def test_csrf_enforced_when_enabled():
    app = create_app({"TESTING": True, "SECRET_KEY": "t", "WTF_CSRF_ENABLED": True})
    with patch("app.mail.requests.post") as post:
        r = app.test_client().post("/contact/", data=GOOD)
    assert r.status_code == 400
    assert "timed out" in r.get_data(as_text=True)
    post.assert_not_called()


# ---- config ----------------------------------------------------------------

def test_production_requires_secret_key(monkeypatch):
    monkeypatch.setenv("APP_ENV", "production")
    monkeypatch.delenv("SECRET_KEY", raising=False)
    with pytest.raises(ConfigError):
        create_app()


def test_production_boots_with_secret(monkeypatch):
    monkeypatch.setenv("APP_ENV", "production")
    monkeypatch.setenv("SECRET_KEY", "abc")
    app = create_app()
    assert app.config["SESSION_COOKIE_SECURE"] is True
    assert app.test_client().get("/").headers.get("Strict-Transport-Security")
