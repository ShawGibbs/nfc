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
    "": "Original",
    "editorial": "Editorial",
    "split": "Split portrait",
    "signature": "Signature",
    "direct": "Contact first",
}


def render(template, destination, **fields):
    source = ROOT / "_templates" / f"{template}.html"
    html = Template(source.read_text(encoding="utf-8")).substitute(fields)
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
    options = "\n".join(
        f'                    <option value="{key}">{label}</option>'
        for key, label in VIEWS.items()
    )
    entries = []
    for slug, contact in CONTACTS.items():
        name = contact.get("display_name", full_name(contact))
        detail = FIRMS[contact["firm"]]["name"] if contact["firm"] == "alliotts" else contact["role"]
        entries.append(
            '                <li class="directory-item">\n'
            f'                    {link(slug + "/", f"{name} – {detail}")}\n'
            '                </li>'
        )
    render("directory", "index.html", options=options, contacts="\n".join(entries))


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
    if office := contact.get("office"):
        details.append(section("Office", "<br>\n            ".join(map(escape, office))))
    return details


def render_card(slug, contact, view=""):
    preview = slug == "template"
    classic_nik = slug == "nik" and not view
    firm_key = contact["firm"]
    firm = FIRMS[firm_key]
    assets = "../../assets/" if view else "../assets/"
    profile = contact.get("profile", firm["website"])
    name = contact.get("display_name", full_name(contact))
    logo = f'<img src="{assets}{firm["logo"]}" alt="{firm["name"]}" class="firm-logo">'
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
        download_url = "../contact.vcf" if view else "contact.vcf"
        download = "" if classic_nik else " download"
        profile_label = "View profile" if "profile" in contact else "Firm website"
        external = ' target="_blank" rel="noopener noreferrer"' if slug == "nik" else ""
        save_attributes = ' class="btn primary"' + download
        profile_attributes = ' class="btn"' + external
        buttons = (
            '        <div class="button-row">\n'
            f'            {link(download_url, "Save contact", save_attributes)}\n'
            f'            {link(profile, profile_label, profile_attributes)}\n'
            '        </div>'
        )
        if view == "direct":
            details.insert(0, buttons)
        else:
            details.append(buttons)

    classes = "classic-nik" if classic_nik else "contact-card"
    navigation = ""
    frame_start = frame_end = ""
    if view:
        classes += f" nik-design {view}"
        frame_start, frame_end = '<div class="design-frame">', '</div>'
        links = [
            link(f"../{key}/" if key else "../", label, ' aria-current="page"' if key == view else "")
            for key, label in list(VIEWS.items())[1:] + [("", VIEWS[""])]
        ]
        navigation = '<nav class="design-nav" aria-label="Nik card designs">\n    ' + "\n    ".join(links) + "\n</nav>"
    elif preview:
        frame_start, frame_end = '<div class="design-frame">', '</div>'
        brand_options = "\n".join(
            f'        <option value="{key}" data-logo="{assets}{brand["logo"]}">{brand["name"]}</option>'
            for key, brand in FIRMS.items()
        )
        navigation = f'''<div class="template-controls">
    <label for="template-firm">Firm</label>
    <select id="template-firm">
{brand_options}
    </select>
    <a href="../">Contact directory</a>
</div>'''

    scripts = [f'<script src="{assets}scripts.js"></script>'] if not preview else []
    if not classic_nik:
        if not view:
            scripts.insert(0, f'<script src="{assets}contact-view.js" defer></script>')
        if contact.get("portrait"):
            scripts.insert(1 if not view else 0, f'<script src="{assets}nik-designs.js" defer></script>')
    render(
        "card", Path(slug) / view / "index.html",
        page_title=escape(full_name(contact) if not preview else "Blank template"),
        assets=assets, firm=firm_key, classes=classes, logo=logo, name=escape(name),
        role=escape(contact["role"]), portrait=portrait, card_body="\n".join(details),
        frame_start=frame_start, frame_end=frame_end, navigation=navigation,
        extra_styles="" if classic_nik else f'    <link rel="stylesheet" href="{assets}nik-designs.css">\n',
        scripts="\n".join(scripts) + "\n",
    )


def vcard_text(text):
    return text.replace("\\", "\\\\").replace("\n", "\\n").replace(";", "\\;").replace(",", "\\,")


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
    fields.extend((f'URL:{contact.get("profile", firm["website"])}', "END:VCARD"))
    (ROOT / slug / "contact.vcf").write_bytes(("\r\n".join(fields) + "\r\n").encode("utf-8"))


if __name__ == "__main__":
    render_directory()
    for slug, contact in CONTACTS.items():
        render_card(slug, contact)
        if slug == "nik":
            for view in list(VIEWS)[1:]:
                render_card(slug, contact, view)
        else:
            write_vcard(slug, contact)
    render_card("template", {
        "firm": "shaw-gibbs", "given_name": "", "family_name": "",
        "display_name": "[Name]", "role": "[Job title]",
    })
