Apartment Guide — Multi-property support (v2.4)

This repository contains a guest guide website for short-term rentals with multi-property support using one shared UI and one codebase. Properties are selected by the `property` URL query parameter (for example `?property=apt-1`).

**v2.4 Updates:**
- Removed the "apt-3" listing (2 active properties remain: apt-1, apt-2)
- Removed the airport transfer section from accommodation info
- Added offline support: the site is installable and cached content keeps working without a connection
- Optimized property and dataset images for much faster loading
- Removed the header property switcher — guests only ever see their own apartment; switch properties by changing the `property` query param directly (host use only)

Quick start

- Open `index.html` or any page in a browser, e.g. `file://.../apartment_guide/index.html`.
- Append `?property=apt-1` to the URL to load a specific property.

How it works

- Property list: `data/properties.json` defines available properties.
- Property content: `data/properties/<property>/content.en.json`, `content.gr.json` and `property.json` contain per-property content and metadata.
- The site preserves `property` in internal links, so a guest stays on their own apartment's pages throughout their visit. There is no guest-facing property switcher; to preview a different property, change the `property` query param in the URL directly.

Developer notes

- To add a new property: create a folder under `data/properties/` with `content.en.json`, `content.gr.json` and `property.json`. Then add an entry to `data/properties.json`.
- The main entry point for behavior is `assets/js/app.js` (functions: `getCurrentProperty()`, `withPropertyParam(url)`, `getPropertyDatasetPath(propertyId)`).

Property structure

- Each property lives under `data/properties/<property-id>/`.
- `property.json` stores property metadata such as `id`, `name`, `address`, `coordinates`, `mapLink`, `rateUsUrl`, `host`, and `heroImage`. `heroImage` is only ever displayed at ~150px wide in the header, so keep it a small, compressed JPEG (see `apt-1`/`apt-2` for the pattern) rather than a full-resolution photo.
- `content.en.json` and `content.gr.json` store guest-facing property content, including accommodation details, Wi-Fi details, house rules, contacts, and neighborhood text.
- Put each apartment's Google review URL in `data/properties/<property-id>/property.json` under `rateUsUrl`.

Accommodation subsection photos

- Some accommodation subsections show a photo next to their text (side by side on wide screens, stacked underneath on phones): Check-in, AC, Parking, Beach Faucet, Breakfast, BBQ, Board Games, Consumables, Iron, Hair Dryer and Laundry.
- Each photo lives at `data/properties/<property-id>/images/accommodation/<section-id>.<ext>`, where `<section-id>` is one of `checkin`, `ac`, `parking`, `beach`, `breakfast`, `bbq`, `games`, `consumables`, `iron`, `hairdryer`, `laundry`. The file name has to match the section id exactly (lowercase, no suffixes) — a camera export like `BBQ.png` or `parking2.png` is never found.
- `.jpg`, `.png` and `.svg` are tried in that order, so to publish a real photo just drop `ac.jpg` next to the shipped `ac.svg` placeholder — no JSON change needed. Delete the `.svg` once every apartment has its real photo. A subsection with no photo at all renders as plain text.
- Resize before committing: `sips -Z 800 -s format jpeg -s formatOptions 80 <src> --out <section-id>.jpg`. 800px wide is plenty for the 240px desktop slot and the full-width phone layout, and keeps each photo around 100–200KB. Full-resolution camera files are never committed; if you keep a local `images/accommodation/originals/` folder to re-crop from, it is gitignored.
- The Wi-Fi QR code works the same way: `data/properties/<property-id>/images/<property-id>-wifi.<ext>` (apt-1 currently ships an `.svg` placeholder; apt-2 has the real `.png`). A different path can be set per property in `content.<lang>.json` under `pages.wifi.qrImage`.

Offline support

- `manifest.json` and `sw.js` (site root) make the guide installable and usable offline. `sw.js` precaches the shared app shell on first visit and caches each guest's own property data/images at runtime as they browse.
- `app.js` rewrites the manifest's `start_url`/name per property at runtime (via a Blob URL) so "Add to Home Screen" installs an icon that opens directly to the guest's own apartment.
- Dataset photos referenced from `dataset/*.json` should point at the resized copies under each category's `optimized/` subfolder (e.g. `dataset/images/beaches/optimized/<file>.jpg`); the un-resized originals are kept alongside for reference but are not served.

Beach distance matrix

- Beaches now use a static driving distance matrix stored in `data/beach_distance_matrix.json`.
- Source beach data lives in `dataset/beaches.json`. Each beach should have stable `id`, `mapLink`, and `coordinates`.
- The generation script is `../scripts/generate_beach_distances.py` from this folder, or `scripts/generate_beach_distances.py` from the workspace root.
- The script first tries to extract coordinates from Google Maps URLs using `extractCoordsFromGoogleMapsUrl(url)`. If that fails, it uses the explicit `coordinates` stored in JSON.
- Driving distances and times are generated offline with OSRM and written to the static JSON file used by the frontend.

Regenerate distances

- Re-run the matrix generator whenever you add a property, change property coordinates, add a beach, or update beach coordinates.
- Example command from the workspace root: `python scripts/generate_beach_distances.py`
