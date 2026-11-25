"""Render the static directory, contact cards, and vCard downloads."""

import json
from html import escape
from pathlib import Path
from string import Template


ROOT = Path(__file__).resolve().parent
DATA = json.loads((ROOT / "data/contacts.json").read_text(encoding="utf-8"))
FIRMS = DATA["firms"]
CONTACTS = DATA["contacts"]
VIEWS = {
    "original": "Original",
    "editorial": "Editorial",
    "split": "Split portrait",
    "signature": "Signature",
    "direct": "Contact first",
}
DEFAULT_VIEW = DATA["default_view"]
ASSETS = "../assets/"


def template(filename, **fields):
    source = ROOT / "_templates" / f"{filename}.html"
    return Template(source.read_text(encoding="utf-8")).substitute(fields)


def write_page(destination, html):
    destination = ROOT / destination
    destination.parent.mkdir(parents=True, exist_ok=True)
    destination.write_text(html, encoding="utf-8")


def link(url, label, attributes=""):
    return f'<a href="{escape(url)}"{attributes}>{escape(label)}</a>'


def section(label, content):
    return (
        '        <div class="section">\n'
        f'            <div class="label">{label}</div>\n'
        f'            {content}\n'
        '        </div>'
    )


def full_name(contact):
    return f'{contact["given_name"]} {contact["family_name"]}'


def render_directory():
    entries = []
    for slug, contact in CONTACTS.items():
        name = contact.get("display_name", full_name(contact))
        summary = f'{name} – {contact["role"]}'
        entries.append(
            '                <li class="directory-item">\n'
            f'                    {link(slug + "/", summary)}\n'
            '                </li>'
        )
    write_page("index.html", template("directory", contacts="\n".join(entries)))


def get_office(contact):
    if "office" in contact:
        return FIRMS[contact["firm"]]["offices"][contact["office"]]
    return {}


def contact_sections(contact, website):
    details = []
    if email := contact.get("email"):
        details.append(section("Email", link(f"mailto:{email}", email)))
    if phone := contact.get("phone"):
        details.append(section("Telephone", link(f"tel:{phone}", contact.get("phone_display", phone))))
    if linkedin := contact.get("linkedin"):
        external = ' target="_blank" rel="noopener noreferrer"'
        details.append(section("Online", "<br>\n            ".join((
            link(website, "Website", external),
            link(linkedin, "LinkedIn", external),
        ))))
    if office := get_office(contact):
        parts = ("street", "extended", "city", "region", "postcode", "country")
        address = "<br>\n            ".join(escape(office[key]) for key in parts if office.get(key))
        details.append(section("Office", address))
    return details


def render_actions(contact, firm, preview, classic_nik):
    if preview:
        save = '<span class="btn primary">Save contact</span>'
        profile = '<span class="btn">View profile</span>'
    else:
        save_attributes = ' class="btn primary"' if classic_nik else ' class="btn primary" download'
        external = ' target="_blank" rel="noopener noreferrer"' if classic_nik else ""
        profile_attributes = ' class="btn"' + external
        profile_url = contact.get("profile", firm["website"])
        profile_label = "View profile" if "profile" in contact else "Firm website"
        save = link("contact.vcf", "Save contact", save_attributes)
        profile = link(profile_url, profile_label, profile_attributes)
    return f'        <div class="button-row">\n            {save}\n            {profile}\n        </div>'


def render_preview_controls(firm_key):
    def selected(condition):
        return " selected" if condition else ""

    view_options = "\n".join(
        f'            <option value="{key}"{selected(key == DEFAULT_VIEW)}>{label}</option>'
        for key, label in VIEWS.items()
    )
    firm_options = "\n".join(
        f'            <option value="{escape(key)}" data-logo="{escape(ASSETS + brand["logo"])}"'
        f'{selected(key == firm_key)}>{escape(brand["name"])}</option>'
        for key, brand in FIRMS.items()
    )
    return template(
        "preview-controls", view_options=view_options, firm_options=firm_options,
        default_view=VIEWS[DEFAULT_VIEW],
    ).rstrip()


def render_card(slug, contact, *, preview=False):
    view = DEFAULT_VIEW
    classic_nik = slug == "nik" and view == "original"
    firm_key = contact["firm"]
    firm = FIRMS[firm_key]
    name = contact.get("display_name", full_name(contact))
    logo = f'<img src="{escape(ASSETS + firm["logo"])}" alt="{escape(firm["name"])}" class="firm-logo">'
    portrait = ""
    if url := contact.get("portrait"):
        attributes = f'alt="{escape(name)}"' if classic_nik else 'alt="" width="220" height="220" hidden'
        portrait = f'<img src="{escape(url)}" class="profile-photo" {attributes}>'
    if not classic_nik:
        initials = "Photo" if preview else contact["given_name"][0] + contact["family_name"][0]
        fallback = f'<span class="portrait-fallback" aria-hidden="true">{escape(initials)}</span>'
        portrait = "\n        ".join(filter(None, (portrait, fallback)))

    if preview:
        details = [
            section("Email", '<span class="placeholder">[Email address]</span>'),
            section("Telephone", '<span class="placeholder">[Telephone number]</span>'),
            section("Online", '<span class="placeholder">[Profile or website]</span>'),
            section("Office", '<span class="placeholder">[Office address]</span>'),
        ]
    else:
        details = contact_sections(contact, firm["website"])
    actions = render_actions(contact, firm, preview, classic_nik)
    if view == "direct":
        details.insert(0, actions)
    else:
        details.append(actions)

    classes = "classic-nik" if classic_nik else "contact-card"
    frame_start = frame_end = ""
    if view != "original":
        classes += f" card-design {view}"
    if view != "original" or preview:
        frame_start, frame_end = '<div class="design-frame">', '</div>'

    scripts = []
    if preview:
        scripts.append(f'<script src="{ASSETS}template-preview.js" defer></script>')
    else:
        if contact.get("portrait") and not classic_nik:
            scripts.append(f'<script src="{ASSETS}card-portrait.js" defer></script>')
        if contact.get("email"):
            scripts.append(f'<script src="{ASSETS}scripts.js"></script>')

    html = template(
        "card",
        page_title=escape("Blank template" if preview else full_name(contact)),
        assets=ASSETS, firm=escape(firm_key), classes=classes, logo=logo, name=escape(name),
        role=escape(contact["role"]), portrait=portrait, card_body="\n".join(details),
        frame_start=frame_start, frame_end=frame_end,
        preview_controls=render_preview_controls(firm_key) if preview else "",
        extra_styles="" if classic_nik else f'    <link rel="stylesheet" href="{ASSETS}card-designs.css">\n',
        scripts="\n".join(scripts) + "\n",
    )
    write_page(Path(slug) / "index.html", html)


def vcard_text(text):
    return text.replace("\\", "\\\\").replace("\n", "\\n").replace(";", "\\;").replace(",", "\\,")


def fold_vcard_line(line):
    folded = []
    part = bytearray()
    for character in line:
        encoded = character.encode("utf-8")
        if len(part) + len(encoded) > 75:
            folded.append(bytes(part))
            part = bytearray(b" ")
        part.extend(encoded)
    folded.append(bytes(part))
    return b"\r\n".join(folded)


def write_vcard(slug, contact):
    firm = FIRMS[contact["firm"]]
    family = vcard_text(contact["family_name"])
    given = vcard_text(contact["given_name"])
    fields = [
        "BEGIN:VCARD",
        "VERSION:3.0",
        f"N:{family};{given};;;",
        f"FN:{vcard_text(full_name(contact))}",
        f"ORG:{vcard_text(firm['name'])}",
        f"TITLE:{vcard_text(contact['role'])}",
    ]
    if phone := contact.get("phone"):
        fields.append(f"TEL;TYPE=WORK,VOICE:{phone}")
    if email := contact.get("email"):
        fields.append(f"EMAIL;TYPE=WORK,INTERNET:{email}")
    if linkedin := contact.get("linkedin"):
        fields.append(f"X-SOCIALPROFILE;TYPE=linkedin:{linkedin}")
    if office := get_office(contact):
        parts = ("po_box", "extended", "street", "city", "region", "postcode", "country")
        address = ";".join(vcard_text(office.get(key, "")) for key in parts)
        fields.append(f"ADR;TYPE=WORK:{address}")
    fields.extend((f'URL;TYPE=WORK:{contact.get("profile", firm["website"])}', "END:VCARD"))
    body = b"\r\n".join(map(fold_vcard_line, fields)) + b"\r\n"
    (ROOT / slug / "contact.vcf").write_bytes(body)


if __name__ == "__main__":
    if DEFAULT_VIEW not in VIEWS:
        raise SystemExit(f'Unknown default_view "{DEFAULT_VIEW}". Choose from {", ".join(VIEWS)}.')
    render_directory()
    for slug, contact in CONTACTS.items():
        render_card(slug, contact)
        write_vcard(slug, contact)
    render_card("template", {
        "firm": next(iter(FIRMS)), "given_name": "", "family_name": "",
        "display_name": "[Name]", "role": "[Job title]",
    }, preview=True)
