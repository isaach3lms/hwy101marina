"""Brand tokens. The sole theming lever: templates and CSS read these as
CSS custom properties, so a reskin is an edit to this file only.

Colors come from the live WordPress site's Elementor global palette
(orange #FF5003, indigo #1E0ECC, sky #6EC1E4, paper #F8FCFE). Ink is the
navy used behind the white logo.
"""

BRAND = {
    "colors": {
        "ink": "#0B1B3F",
        "ink-soft": "#16295A",
        "indigo": "#1E0ECC",
        "orange": "#FF5003",
        "orange-dark": "#E04400",
        "sky": "#6EC1E4",
        "paper": "#F8FCFE",
        "white": "#FFFFFF",
        "text": "#1F2A44",
        "muted": "#5B6785",
        "line": "#DCE6F2",
        "sand": "#FFBC7D",
    },
    "fonts": {
        "heading": '"Poppins", system-ui, -apple-system, "Segoe UI", sans-serif',
        "body": '"Open Sans", system-ui, -apple-system, "Segoe UI", sans-serif',
    },
    "google_fonts_url": (
        "https://fonts.googleapis.com/css2?family=Open+Sans:wght@400;600"
        "&family=Poppins:wght@500;700&display=swap"
    ),
    "radius": "14px",
    "logo": "img/brand/logo.png",
    "logo_small": "img/brand/logo-small.png",
    "og_image": "img/brand/og-card.jpg",
}


def css_tokens() -> str:
    """Render the :root block injected into base.html."""
    lines = [f"--{name}: {value};" for name, value in BRAND["colors"].items()]
    lines.append(f"--font-heading: {BRAND['fonts']['heading']};")
    lines.append(f"--font-body: {BRAND['fonts']['body']};")
    lines.append(f"--radius: {BRAND['radius']};")
    return ":root{" + "".join(lines) + "}"
