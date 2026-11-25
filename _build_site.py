"""Build all public language pages from the shared layout and translations."""
from html import escape
import json
from pathlib import Path
from string import Template

ROOT = Path(__file__).resolve().parent
SITE_URL = "https://game-de-it.github.io/last-emulator-web/"
RELEASE_VERSION = "1.0.3"
RELEASE_REPO = "https://github.com/game-de-it/last-emulator-web"

LANGUAGES = [
    ("ja", "ja", "日本語"),
    ("en", "en", "English"),
    ("zh-hans", "zh-Hans", "简体中文"),
    ("id", "id", "Bahasa Indonesia"),
    ("pt-br", "pt-BR", "Português (Brasil)"),
    ("es-419", "es-419", "Español (Latinoamérica)"),
    ("fil", "fil", "Filipino"),
    ("vi", "vi", "Tiếng Việt"),
    ("ko", "ko", "한국어"),
]

MARKUP_KEYS = {"handheld_body", "produced", "contact"}


def route(code):
    return "" if code == "ja" else f"{code}/"


def language_switcher(code, language_name, heading, prefix):
    links = []
    for choice, tag, label in LANGUAGES:
        current = ' aria-current="page"' if code == choice else ''
        href = prefix + route(choice) or './'
        links.append(f'<li><a href="{href}" lang="{tag}" hreflang="{tag}"{current}>{escape(label)}</a></li>')
    return (
        '<details class="language-switcher">'
        f'<summary aria-label="{escape(heading)}: {escape(language_name)}">{escape(language_name)}</summary>'
        f'<ul aria-label="{escape(heading)}">{"".join(links)}</ul></details>'
    )


def main():
    template = Template((ROOT / "_site_template.html").read_text(encoding="utf-8"))
    release_tag = f"v{RELEASE_VERSION}"
    release_page = f"{RELEASE_REPO}/releases/tag/{release_tag}"
    shared = {
        "site_url": SITE_URL,
        "version": release_tag,
        "release_num": RELEASE_VERSION,
        "release_page": release_page,
        "release_download": f"{RELEASE_REPO}/releases/download/{release_tag}",
    }
    alternatives = "\n    ".join(
        f'<link rel="alternate" hreflang="{tag}" href="{SITE_URL}{route(code)}">'
        for code, tag, _ in LANGUAGES
    )
    expected_keys = None
    for code, tag, language_name in LANGUAGES:
        locale = json.loads((ROOT / "_locales" / f"{code}.json").read_text(encoding="utf-8"))
        if expected_keys is None:
            expected_keys = locale.keys()
        if locale.keys() != expected_keys or any(not value.strip() for value in locale.values()):
            raise ValueError(f"{code} has missing, blank, or unexpected translation keys")
        prefix = "../" if route(code) else "./"
        canonical = SITE_URL + route(code)
        seo = (
            f'<link rel="canonical" href="{canonical}">\n    '
            f'<meta property="og:url" content="{canonical}">\n    '
            f'{alternatives}\n    <link rel="alternate" hreflang="x-default" href="{SITE_URL}">'
        )
        trans = {}
        for key, value in locale.items():
            text = Template(value).substitute(shared)
            trans[key] = text if key in MARKUP_KEYS else escape(text)
        for key in ("overview_body", "craft_intro", "craft_color", "streaming_body"):
            trans[key] = trans[key].replace("Last Emulator", "<strong>Last Emulator</strong>")
        html = template.substitute(
            **shared, **trans, lang=tag, prefix=prefix, seo_links=seo,
            language_switcher=language_switcher(code, language_name, locale["language"], prefix)
        )
        directory = ROOT / route(code)
        directory.mkdir(exist_ok=True)
        (directory / "index.html").write_text(html, encoding="utf-8")


if __name__ == "__main__":
    main()
