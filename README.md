# NFC contact cards

Edit `data/contacts.json` to add or update a contact. The contact’s `firm` selects its logo, firm details, and palette. Brand colours for both firms are in `assets/brands.css`, including dark-mode colours. The templates for the cards and directory are in `_templates/`.

Run `python3 build_cards.py` to regenerate the static pages and downloadable vCards, then commit the generated files with the source changes. Nik’s existing vCard is kept for compatibility. Routes and view URLs work with a static host.

To preview locally, run `python3 -m http.server 8000` from the repository root. The directory links to a blank template where you can switch between firms.
