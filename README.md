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
