"""All site copy and data. Edit text here, never in templates.

Source: migrated from the live WordPress site (hwy101marina.com) in Oct 2026.
Prices were read from the pricing images on the live Rentals page.
"""
import re
from pathlib import Path

SITE = {
    "name": "101 Marina",
    "legal_name": "101 Marina",
    "tagline": "Boat rentals, slips and RV camping on Lake Norfork",
    "phone_display": "(870) 467-5252",
    "phone_tel": "+18704675252",
    "facebook": "https://www.facebook.com/101marina/",
    "locality": "Gamaliel",
    "region": "AR",
    "country": "US",
    "place_line": "Howard Cove, Lake Norfork, Gamaliel, AR",
}

NAV = [
    {"label": "Home", "endpoint": "site.home"},
    {"label": "Rentals", "endpoint": "site.rentals"},
    {"label": "Campground", "endpoint": "site.campground"},
    {"label": "Our Store", "endpoint": "site.store"},
    {"label": "Photo Gallery", "endpoint": "site.gallery"},
    {"label": "Contact", "endpoint": "site.contact"},
]

# Old WordPress paths mapped to the new URLs. Served as 301s so existing
# search rankings and inbound links carry over.
LEGACY_REDIRECTS = {
    "/residential": "/rentals/",
    "/commercial": "/campground/",
    "/ourstore": "/store/",
    "/photogallery": "/gallery/",
    "/sitemap_index.xml": "/sitemap.xml",
    "/page-sitemap.xml": "/sitemap.xml",
    "/post-sitemap.xml": "/sitemap.xml",
}

PAGES = {
    "home": {
        "path": "/",
        "title": "101 Marina | Boat Rentals and RV Camping on Lake Norfork, Gamaliel AR",
        "description": (
            "Full-service marina on Lake Norfork in Gamaliel, AR. Pontoon and tritoon "
            "rentals, RV camping, fuel, an on-site store and eight docks. Call (870) 467-5252."
        ),
    },
    "rentals": {
        "path": "/rentals/",
        "title": "Boat Rentals on Lake Norfork | Pontoons and Tritoons | 101 Marina",
        "description": (
            "Rent a pontoon, tritoon or fishing pontoon by the day at 101 Marina in "
            "Howard Cove on Lake Norfork. See rates and call (870) 467-5252 to book."
        ),
    },
    "campground": {
        "path": "/campground/",
        "title": "RV Camping in Gamaliel, AR | 101 Marina Campground",
        "description": (
            "14 campsites with on-site electric and water hookups and restrooms at "
            "101 Marina on Lake Norfork. RV sites are $20 a day. Call to book."
        ),
    },
    "store": {
        "path": "/store/",
        "title": "Our Store | Fuel, Snacks, Supplies and Bait | 101 Marina",
        "description": (
            "The on-site store at 101 Marina has fuel, snacks, supplies and bait, "
            "plus water toys for rent. Take a look inside."
        ),
    },
    "gallery": {
        "path": "/gallery/",
        "title": "Photo Gallery | 101 Marina on Lake Norfork",
        "description": "Photos of the docks, boats and lake at 101 Marina in Gamaliel, AR.",
    },
    "contact": {
        "path": "/contact/",
        "title": "Contact 101 Marina | Schedule a Call",
        "description": (
            "Schedule a call about a boat rental or camping at 101 Marina on Lake "
            "Norfork, or call (870) 467-5252."
        ),
    },
    "thanks": {
        "path": "/contact/thanks/",
        "title": "Thanks | 101 Marina",
        "description": "We received your request and will call you.",
        "noindex": True,
    },
    "not_found": {
        "path": "/404",
        "title": "Page not found | 101 Marina",
        "description": "That page could not be found.",
        "noindex": True,
    },
}

HOME = {
    "hero_title": "It's time to get your feet wet",
    "hero_body": (
        "Welcome to 101 Marina, a full-service marina complete with boat rentals, "
        "slip rentals, RV camping, and more. Located on Lake Norfork in Gamaliel, AR, "
        "we're an amazing home away from home for tons of families that join us "
        "throughout the year. Visit us and experience the 101 Marina difference."
    ),
    "hero_facts": ["8 marine docks", "Fuel on site", "On-site store", "14 campsites"],
    "tiles_title": "Let us work while you unwind",
    "tiles": [
        {
            "title": "Boating",
            "icon": "yatch.png",
            "endpoint": "site.rentals",
            "body": "Pontoons, tritoons and fishing pontoons, rented by the day.",
        },
        {
            "title": "Camping",
            "icon": "camper-van.png",
            "endpoint": "site.campground",
            "body": "14 campsites with on-site electric, water and restrooms.",
        },
        {
            "title": "And much more!",
            "icon": "map.png",
            "endpoint": "site.store",
            "body": "Fuel, snacks, supplies, bait and water toys at our store.",
        },
    ],
    "needs_title": "We cover all your needs",
    "needs": [
        "8 marine docks",
        "On-site store",
        "Fuel stations",
        "Toys for kids",
        "Great pricing",
        "Easy booking",
    ],
    "visit_title": "Come see us at 101 Marina!",
    "visit_body": (
        "At 101 Marina, we're proud to be a full-service marina! Situated in Howard "
        "Cove on Lake Norfork. We offer boat rentals for those coming and looking to "
        "get out on the water, along with fuel, snacks, supplies and bait. Also don't "
        "forget our water toys, available for rent. Right on the side of a beautiful "
        "lake, we have eight docks available for your use."
    ),
    "visit_button": "Come see inside",
    "cta_title": "Call to book your vacation away today!",
    "cta_button": "Click to call today",
}

# Rates are per day plus tax, read from the pricing images on the live Rentals page.
RENTALS = {
    "title": "Our current available boats",
    "intro": "Rates are per day plus tax. Call to book.",
    "boats": [
        {
            "name": "24' Godfrey Pontoon",
            "note": "3 to choose from",
            "hp": 140,
            "capacity": 12,
            "price": 375,
            "image": "boat-1.jpg",
        },
        {
            "name": "26' Godfrey Tritoon with Slide",
            "note": "",
            "hp": 200,
            "capacity": 16,
            "price": 485,
            "image": "boat-2.jpg",
        },
        {
            "name": "26' Godfrey Tritoon with Slide",
            "note": "",
            "hp": 200,
            "capacity": 16,
            "price": 485,
            "image": "boat-3.jpg",
        },
        {
            "name": "21' Lowe",
            "note": "",
            "hp": 115,
            "capacity": 11,
            "price": 295,
            "image": "boat-4.jpg",
        },
        {
            "name": "21' Lowe Fishing Pontoon",
            "note": "",
            "hp": 115,
            "capacity": 11,
            "price": 285,
            "image": "boat-5.jpg",
        },
        {
            "name": "20' Suntracker Fishing Pontoon",
            "note": "",
            "hp": 90,
            "capacity": 10,
            "price": 285,
            "image": "boat-7.jpg",
        },
        {
            "name": "Bennington Tritoon with Slide",
            "note": "",
            "hp": 250,
            "capacity": 12,
            "price": 575,
            "image": "boat-6.jpg",
        },
    ],
    "strip_title": "Get your feet wet with one of our rentals",
    "strip": [
        {"label": "Marine docks", "icon": "shipping.png"},
        {"label": "On-site store", "icon": "shop.png"},
        {"label": "Fuel stations", "icon": "gasoline-pump.png"},
        {"label": "Toys for kids", "icon": "beach-ball.png"},
    ],
    "needs_title": "We cover all your needs",
    "needs_body": HOME["visit_body"],
    "gallery_button": "View gallery",
    "cta_title": "Call to book your vacation away today!",
    "cta_button": "Call to book today",
}

CAMPGROUND = {
    "title": "Your vacation destination away from home",
    "features": [
        {"label": "14 campsites available", "icon": "camper-van.png"},
        {"label": "On-site electric and water hookups", "icon": "sustainable-energy-water-2.png"},
        {"label": "On-site restrooms available", "icon": "toilet-1.png"},
        {"label": "Nearby attractions and accessories", "icon": "town.png"},
    ],
    "heading": "Campsites available in Gamaliel, AR",
    "body": (
        "We are prepared to welcome you to our location, whatever your interests may "
        "be. A number of sites are available to meet your needs for your tent and RV. "
        "Camping here is a comfortable and pleasant vacation."
    ),
    "sites": [{"name": "RV camp site", "price": 20, "unit": "Daily"}],
    "cta_title": "Call to book your vacation away today!",
    "cta_button": "Click to call today",
}

STORE = {
    "title": "Our store",
    "intro": (
        "Our on-site store keeps you stocked for the day on the water: fuel, snacks, "
        "supplies and bait. Water toys are also available for rent."
    ),
    "cta_title": "Come see us at 101 Marina",
    "cta_button": "Call us",
}

GALLERY_PAGE = {
    "title": "Photo gallery",
    "intro": "The docks, the boats and the lake.",
}

CONTACT = {
    "title": "Contact us and enjoy your time off",
    "form_title": "Schedule a call",
    "interests": [("boating", "Boating rental"), ("camping", "Camping rental")],
    "steps": ["Submit your form", "We'll call you", "Book your rental"],
    "thanks_title": "Thanks, we got your request",
    "thanks_body": "We will call you at the number you gave us. Need a boat today? Call us directly.",
    "error_body": "We could not send your request just now. Please call us directly.",
}

# ---- Gallery data -----------------------------------------------------------
# Slugs match files in static/img/gallery. Order matches the live gallery page.
_GALLERY_ORDER = [
    "dsc01259", "dsc01416", "dsc-0836", "dsc01383", "dsc-0005", "dsc-1000",
    "dsc01222", "dsc-0993", "dsc-0819", "dsc-0975", "dsc01231", "dsc01438",
    "dsc-0977", "dsc01329", "dsc01234", "dsc01315", "dsc01351", "dsc-0983",
    "dsc-0726", "dsc-0725", "dsc-0683", "dsc-0679", "dsc-0064", "dsc-0063",
    "dsc-0062", "dsc-0061", "dsc-0059", "dsc-0057", "dsc-0054", "dsc-0052",
    "dsc-0047", "dsc-0046", "dsc-0044", "dsc-0041", "dsc-0040", "dsc-0623",
]
# Subset shown on the Our Store page, in live order.
_STORE_ORDER = [
    "dsc-0726", "dsc-0052", "dsc-0061", "dsc-0062", "dsc-0063", "dsc-0064",
    "dsc-0725", "dsc-0046", "dsc-0683", "dsc-0679", "dsc-0047", "dsc-0057",
    "dsc-0044", "dsc-0040", "dsc-0041", "dsc-0054", "dsc-0059",
]

_MANIFEST_RE = re.compile(r"-> (\S+)\.jpg (\d+)x(\d+)")


def _dimensions() -> dict:
    manifest = Path(__file__).parent / "static" / "img" / "gallery" / "MANIFEST.txt"
    dims = {}
    if manifest.exists():
        for line in manifest.read_text().splitlines():
            m = _MANIFEST_RE.search(line)
            if m:
                dims[m.group(1)] = (int(m.group(2)), int(m.group(3)))
    return dims


def _photos(order, label):
    dims = _dimensions()
    out = []
    for i, slug in enumerate(order, start=1):
        w, h = dims.get(slug, (1600, 1067))
        out.append(
            {
                "full": f"img/gallery/{slug}.jpg",
                "thumb": f"img/gallery/thumbs/{slug}.jpg",
                "thumb_w": 640,
                "thumb_h": round(640 * h / w),
                "alt": f"{label}, photo {i} of {len(order)}",
            }
        )
    return out


GALLERY_PHOTOS = _photos(_GALLERY_ORDER, "101 Marina on Lake Norfork")
STORE_PHOTOS = _photos(_STORE_ORDER, "Inside the 101 Marina store")
HOME_PHOTOS = _photos(["dsc01259", "dsc-0836", "dsc01383", "dsc-0005", "dsc01222", "dsc-0975"], "101 Marina on Lake Norfork")
