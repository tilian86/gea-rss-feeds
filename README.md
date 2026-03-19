# GEA RSS Feeds

Generiert RSS-Feeds für die Ressort-Seiten des Reutlinger General-Anzeigers (gea.de), die offiziell keine RSS-Feeds anbieten.

## Verfügbare Feeds

| Feed | Quelle |
|------|--------|
| `reutlingen.xml` | [gea.de/reutlingen.html](https://www.gea.de/reutlingen.html) |
| `tuebingen.xml` | [gea.de/neckar-alb/kreis-tuebingen.html](https://www.gea.de/neckar-alb/kreis-tuebingen.html) |

## Setup

### 1. GitHub Repo erstellen

- Neues Repository auf GitHub anlegen (z.B. `gea-rss-feeds`)
- Kann **public** oder **private** sein (Pages geht bei beiden)

### 2. Dateien hochladen

Alle Dateien aus diesem Ordner ins Repo pushen:

```bash
cd gea-rss-feeds
git init
git add .
git commit -m "Initial commit"
git remote add origin https://github.com/DEIN-USERNAME/gea-rss-feeds.git
git branch -M main
git push -u origin main
```

### 3. GitHub Pages aktivieren

1. Im Repo → **Settings** → **Pages**
2. Source: **GitHub Actions** (nicht "Deploy from a branch")
3. Speichern

### 4. Ersten Build auslösen

1. Im Repo → **Actions** → **GEA RSS Feed Update**
2. **Run workflow** klicken

### 5. Feed-URLs in Feedly eintragen

Nach dem ersten erfolgreichen Build sind die Feeds erreichbar unter:

```
https://DEIN-USERNAME.github.io/gea-rss-feeds/reutlingen.xml
https://DEIN-USERNAME.github.io/gea-rss-feeds/tuebingen.xml
```

Diese URLs einfach in Feedly als neue Quelle hinzufügen.

## Aktualisierung

Der Feed wird automatisch alle 30 Minuten zwischen 06:00 und 00:00 Uhr (MEZ/MESZ) aktualisiert via GitHub Actions.

## Lokal testen

```bash
pip install -r requirements.txt
python scrape.py
```

Die generierten Feeds landen im `feeds/`-Ordner.
