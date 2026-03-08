Apartment Guide — Multi-property support

This repository contains a guest guide website for short-term rentals. Changes in this branch add multi-property support using one shared UI and one codebase. Properties are selected by the `property` URL query parameter (for example `?property=apt-1`).

Quick start

- Open `index.html` or any page in a browser, e.g. `file://.../apartment_guide/index.html`.
- Append `?property=apt-1` to the URL to load a specific property.

How it works

- Property list: `data/properties.json` defines available properties.
- Property content: `data/properties/<property>/content.en.json`, `content.gr.json` and `property.json` contain per-property content and metadata.
- The site preserves `property` in internal links. The header includes a property dropdown to switch properties while preserving language.

Developer notes

- To add a new property: create a folder under `data/properties/` with `content.en.json`, `content.gr.json` and `property.json`. Then add an entry to `data/properties.json`.
- The main entry point for behavior is `assets/js/app.js` (functions: `getCurrentProperty()`, `withPropertyParam(url)`, `getPropertyDatasetPath(propertyId)`).

Property structure

- Each property lives under `data/properties/<property-id>/`.
- `property.json` stores property metadata such as `id`, `name`, `address`, `coordinates`, `mapLink`, `rateUsUrl`, `host`, and `heroImage`.
- `content.en.json` and `content.gr.json` store guest-facing property content, including accommodation details, Wi-Fi details, house rules, contacts, and neighborhood text.
- Put each apartment's Google review URL in `data/properties/<property-id>/property.json` under `rateUsUrl`.

Beach distance matrix

- Beaches now use a static driving distance matrix stored in `data/beach_distance_matrix.json`.
- Source beach data lives in `dataset/beaches.json`. Each beach should have stable `id`, `mapLink`, and `coordinates`.
- The generation script is `../scripts/generate_beach_distances.py` from this folder, or `scripts/generate_beach_distances.py` from the workspace root.
- The script first tries to extract coordinates from Google Maps URLs using `extractCoordsFromGoogleMapsUrl(url)`. If that fails, it uses the explicit `coordinates` stored in JSON.
- Driving distances and times are generated offline with OSRM and written to the static JSON file used by the frontend.

Regenerate distances

- Re-run the matrix generator whenever you add a property, change property coordinates, add a beach, or update beach coordinates.
- Example command from the workspace root: `python scripts/generate_beach_distances.py`
