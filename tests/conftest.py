import pytest

from app import create_app


@pytest.fixture()
def app():
    return create_app(
        {
            "TESTING": True,
            "SECRET_KEY": "test",
            "WTF_CSRF_ENABLED": False,
            "SITE_URL": "https://www.hwy101marina.com",
            "RESEND_API_KEY": "",
            "MAIL_FROM": "",
            "MAIL_TO": [],
        }
    )


@pytest.fixture()
def client(app):
    return app.test_client()
