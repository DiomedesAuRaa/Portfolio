#!/usr/bin/env python3
"""
fetch_feeds.py
Runs in GitHub Actions. Reads sub.yaml, parses each RSS feed,
and writes podcast-manifest.json for the HTML player to consume.
No audio downloading — just metadata + direct audio URLs.
"""

import json
import yaml
import feedparser
from datetime import datetime
import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
SUBS_FILE = os.path.join(BASE_DIR, "sub.yaml")
MANIFEST_FILE = os.path.join(BASE_DIR, "podcast-manifest.json")
MAX_EPISODES = 5

with open(SUBS_FILE, "r") as f:
    subs = yaml.safe_load(f)["podcasts"]

def format_date(parsed_time):
    if not parsed_time:
        return ""
    try:
        return datetime(*parsed_time[:6]).strftime("%b %d, %Y")
    except Exception:
        return ""

def sort_date(parsed_time):
    """ISO date string for sorting, e.g. 2025-03-05"""
    if not parsed_time:
        return ""
    try:
        return datetime(*parsed_time[:6]).strftime("%Y-%m-%d")
    except Exception:
        return ""

def get_audio_url(entry):
    if getattr(entry, "enclosures", None):
        try:
            first = entry.enclosures[0]
            url = first.get("href") if isinstance(first, dict) else getattr(first, "href", None)
            if url:
                return url
        except Exception:
            pass
    # fallback to entry link
    return getattr(entry, "link", None)

manifest = []

for sub in subs:
    name = sub["name"]
    feed_url = sub["feed_url"]
    print(f"Fetching: {name}")

    try:
        feed = feedparser.parse(feed_url)
        episodes = []
        for entry in feed.entries[:MAX_EPISODES]:
            audio_url = get_audio_url(entry)
            if not audio_url:
                continue
            episodes.append({
                "title": getattr(entry, "title", "Untitled"),
                "date": format_date(getattr(entry, "published_parsed", None)),
                "dateSort": sort_date(getattr(entry, "published_parsed", None)),
                "audioUrl": audio_url,
            })
        manifest.append({"name": name, "episodes": episodes})
        print(f"  -> {len(episodes)} episodes")
    except Exception as e:
        print(f"  [!] Failed to fetch {name}: {e}")
        manifest.append({"name": name, "episodes": []})

with open(MANIFEST_FILE, "w") as f:
    json.dump(manifest, f, indent=2)

print(f"\nManifest written: {MANIFEST_FILE}")