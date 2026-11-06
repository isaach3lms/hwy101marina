# 101 Marina

Flask rebuild of hwy101marina.com, migrated off WordPress (Elementor) to Render.
Five live pages: Home, Rentals, Campground, Our Store, Photo Gallery. Every call to action is the phone number.

The Contact page is built but switched off (`CONTACT_ENABLED=false` in `render.yaml`). To bring it back, set `CONTACT_ENABLED` to `true` in the Render Environment tab and redeploy. The nav link, sitemap entry and form return with no code change. While off, `/contact/` redirects to the home page.

## Where things live

| To change | Edit |
|---|---|
| Any copy, prices, boats, photos shown | `app/content.py` |
| Colors, fonts, logo paths | `app/brand.py` (the only theming lever) |
| Layout and styling | `app/templates/`, `app/static/css/site.css` |
| Contact form delivery | `app/mail.py` (Resend HTTP API) |

Rental rates and the RV site rate are plain numbers in `app/content.py`.

## Run locally

```
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements-dev.txt
flask --app wsgi run --debug
pytest
```

Without Resend keys, a local contact form submit is logged and treated as delivered.

## Deploy on Render

1. Push this folder to a GitHub repo, branch `main`.
2. In Render: New, Blueprint, pick the repo. `render.yaml` creates the web service. Pushes to `main` auto-deploy.
3. In the service Environment tab, fill the values marked `sync: false`:
   - `WEB3FORMS_ACCESS_KEY`: the contact form posts to Web3Forms from the visitor's browser (their free plan rejects server-side calls). The key is public by design. Leads go to the inbox tied to the key in the Web3Forms dashboard.
   - `RESEND_API_KEY`, `MAIL_FROM` (a sender on a domain verified in Resend), `MAIL_TO` (comma separated inboxes): fallback used if the browser post fails or JavaScript is off. Optional; without them the fallback tells the visitor to call.
4. Open the `.onrender.com` URL and check every page and the contact form.
5. Cutover: in the service Settings, Custom Domains, add `www.hwy101marina.com` and `hwy101marina.com`. Update DNS at the registrar to the records Render shows (they replace the WordPress host records). Render issues TLS automatically.
6. Redirect the bare domain to `www` in Render's custom domain settings so there is one canonical host.

Until the domain is switched, set `SITE_URL` to the `.onrender.com` URL if you want canonical tags and the sitemap to match the preview.

## What carries over from WordPress

- Old URLs 301 to the new ones: `/residential` to `/rentals/`, `/commercial` to `/campground/`, `/ourstore` to `/store/`, `/photogallery` to `/gallery/`, plus the Yoast sitemap URLs to `/sitemap.xml`.
- Page titles and descriptions, a LocalBusiness schema block, sitemap, robots.txt.
- Every photo (resized for web), the logo, the icons, brand colors and fonts.
- Leads sent through the server fallback are also written to the Render service logs. Leads sent through Web3Forms live in the Web3Forms dashboard and the receiving inbox.

## Images

`scripts/optimize_images.py` rebuilds the web-sized images from the original downloads. Originals are not in the repo.
