#!/usr/bin/env python3
"""
GEA RSS Feed Generator
Scrapt die Ressort-Seiten des Reutlinger General-Anzeigers
und erzeugt valide RSS-XML-Dateien für Feedly & Co.
"""

import re
import os
import html
import urllib.parse
from datetime import datetime, timezone
from xml.etree.ElementTree import Element, SubElement, tostring, indent

import requests
from bs4 import BeautifulSoup

# ── Konfiguration ──────────────────────────────────────────────
FEEDS = {
    "reutlingen": {
        "url": "https://www.gea.de/reutlingen.html",
        "title": "GEA – Reutlingen",
        "description": "Nachrichten aus dem Ressort Reutlingen des Reutlinger General-Anzeigers",
        "link": "https://www.gea.de/reutlingen.html",
    },
    "tuebingen": {
        "url": "https://www.gea.de/neckar-alb/kreis-tuebingen.html",
        "title": "GEA – Kreis Tübingen",
        "description": "Nachrichten aus dem Ressort Kreis Tübingen des Reutlinger General-Anzeigers",
        "link": "https://www.gea.de/neckar-alb/kreis-tuebingen.html",
    },
}

BASE_URL = "https://www.gea.de"
OUTPUT_DIR = "feeds"
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) GEA-RSS-Generator/1.0"
}


def scrape_articles(url: str) -> list[dict]:
    """Scrapt Artikel-Teaser von einer GEA-Ressortseite."""
    resp = requests.get(url, headers=HEADERS, timeout=30)
    resp.raise_for_status()
    soup = BeautifulSoup(resp.text, "html.parser")

    articles = []
    seen_urls = set()

    for teaser in soup.select("a.nfy-ar-teaser"):
        # Das <a>-Tag selbst ist der Link
        href = teaser.get("href", "")
        if not href or "_artikel," not in href or href in seen_urls:
            continue
        seen_urls.add(href)

        full_url = href if href.startswith("http") else BASE_URL + href

        # Titel aus h3
        h3 = teaser.select_one("h3")
        title = h3.get_text(strip=True) if h3 else ""
        if not title:
            continue

        # GEA+ Paywall-Marker
        is_plus = "nfy-ar-plus" in str(teaser)
        if is_plus and not title.startswith("GEA+:"):
            title = f"GEA+: {title}"

        # Bild
        img = teaser.select_one("img[data-src]")
        image_url = ""
        if img:
            src = img.get("data-src", "")
            if src:
                image_url = src if src.startswith("http") else BASE_URL + src

        # Artikel-ID aus URL für GUID
        arid_match = re.search(r"_arid,(\d+)", href)
        guid = full_url

        articles.append({
            "title": title,
            "link": full_url,
            "guid": guid,
            "image": image_url,
            "arid": arid_match.group(1) if arid_match else "",
        })

    return articles


def build_rss(feed_config: dict, articles: list[dict]) -> str:
    """Baut eine RSS 2.0 XML-Datei."""
    now = datetime.now(timezone.utc).strftime("%a, %d %b %Y %H:%M:%S +0000")

    rss = Element("rss", version="2.0")
    rss.set("xmlns:atom", "http://www.w3.org/2005/Atom")
    rss.set("xmlns:media", "http://search.yahoo.com/mrss/")

    channel = SubElement(rss, "channel")
    SubElement(channel, "title").text = feed_config["title"]
    SubElement(channel, "link").text = feed_config["link"]
    SubElement(channel, "description").text = feed_config["description"]
    SubElement(channel, "language").text = "de"
    SubElement(channel, "lastBuildDate").text = now
    SubElement(channel, "generator").text = "GEA RSS Feed Generator"

    for article in articles:
        item = SubElement(channel, "item")
        SubElement(item, "title").text = article["title"]
        SubElement(item, "link").text = article["link"]
        SubElement(item, "guid", isPermaLink="true").text = article["guid"]

        if article.get("image"):
            enclosure = SubElement(item, "enclosure")
            enclosure.set("url", article["image"])
            enclosure.set("type", "image/jpeg")
            enclosure.set("length", "0")

    indent(rss, space="  ")
    xml_str = tostring(rss, encoding="unicode", xml_declaration=False)
    return '<?xml version="1.0" encoding="utf-8"?>\n' + xml_str


def main():
    os.makedirs(OUTPUT_DIR, exist_ok=True)

    for name, config in FEEDS.items():
        print(f"Scraping {config['title']}...")
        try:
            articles = scrape_articles(config["url"])
            print(f"  → {len(articles)} Artikel gefunden")

            xml = build_rss(config, articles)
            path = os.path.join(OUTPUT_DIR, f"{name}.xml")
            with open(path, "w", encoding="utf-8") as f:
                f.write(xml)
            print(f"  → {path} geschrieben")

        except Exception as e:
            print(f"  ✗ Fehler: {e}")

    # Index-Seite für GitHub Pages
    index_html = """<!DOCTYPE html>
<html lang="de">
<head><meta charset="utf-8"><title>GEA RSS Feeds</title></head>
<body>
<h1>GEA RSS Feeds</h1>
<ul>
  <li><a href="reutlingen.xml">GEA – Reutlingen</a></li>
  <li><a href="tuebingen.xml">GEA – Kreis Tübingen</a></li>
</ul>
<p>Zuletzt aktualisiert: {now}</p>
</body>
</html>""".format(now=datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC"))

    with open(os.path.join(OUTPUT_DIR, "index.html"), "w", encoding="utf-8") as f:
        f.write(index_html)

    print("\nFertig.")


if __name__ == "__main__":
    main()
