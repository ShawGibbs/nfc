# NFC contact cards

- **Add or update a person.** Edit the `contacts` section of `data/contacts.json`. The key is the public path, such as `josh` for `/josh/`. Set the person’s `firm` and, if applicable, `office` to keys from the firm’s record. Keep phone numbers in international format and use `phone_display` for the on-screen format.
- **Add a firm or office.** Add the firm name, website, logo filename, and any offices under `firms`. Put the logo in `assets/` and add the matching firm palette in `assets/brands.css`. Define each office address once under that firm’s `offices`.
- **Change the layout.** Preview layouts and firm branding on `/template/`. Edit `default_view` in `data/contacts.json` to change the layout for every published card. Edit `_templates/card.html` or the shared CSS to change the template itself.

Run `python3 build_cards.py` after editing data or templates. It updates the directory and generates one page and downloadable vCard per person. Commit the generated files with your edits. To preview locally, run `python3 -m http.server 8000` from the repository root.
