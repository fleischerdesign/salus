#!/usr/bin/env python3
import json
import os
import re
import httpx

MANIFEST_PATH = "vendor_manifest.json"
BASE_STATIC_DIR = "src/salus/static"
VENDOR_DIR = os.path.join(BASE_STATIC_DIR, "vendor")
FONTS_DIR = os.path.join(BASE_STATIC_DIR, "fonts")

# Modern Chrome User Agent to force Google Fonts to return WOFF2 files
CHROME_UA = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"


def main():
    if not os.path.exists(MANIFEST_PATH):
        print(f"Error: {MANIFEST_PATH} not found.")
        return

    with open(MANIFEST_PATH, "r") as f:
        manifest = json.load(f)

    # Ensure directories exist
    os.makedirs(VENDOR_DIR, exist_ok=True)
    os.makedirs(FONTS_DIR, exist_ok=True)

    client = httpx.Client(follow_redirects=True)

    # 1. Download JS Libraries
    print("--- Downloading JS Libraries ---")
    for name, info in manifest.get("libraries", {}).items():
        version = info["version"]
        url = info["url"].format(version=version)
        target = info["target"]
        
        # Ensure target's parent directory exists
        os.makedirs(os.path.dirname(target), exist_ok=True)

        print(f"Downloading {name} v{version} from {url}...")
        try:
            resp = client.get(url)
            resp.raise_for_status()
            with open(target, "wb") as out_f:
                out_f.write(resp.content)
            print(f"Saved {name} to {target}")
        except Exception as e:
            print(f"Failed to download {name}: {e}")

    # 2. Download and Localize Fonts
    print("\n--- Localizing Fonts ---")
    combined_css = []
    
    for font_info in manifest.get("fonts", []):
        name = font_info["name"]
        css_url = font_info["css_url"]
        print(f"Fetching Google Fonts CSS for {name}...")

        try:
            resp = client.get(css_url, headers={"User-Agent": CHROME_UA})
            resp.raise_for_status()
            css_content = resp.text

            # Find all gstatic font URLs (e.g. url(https://fonts.gstatic.com/...))
            font_urls = re.findall(r"url\((https://fonts\.gstatic\.com/[^)]+)\)", css_content)
            print(f"Found {len(font_urls)} font file references for {name}.")

            for url in font_urls:
                # Extract filename from URL (e.g. .../s/manrope/v15/filename.woff2)
                filename = url.split("/")[-1]
                target_font_path = os.path.join(FONTS_DIR, filename)

                print(f"  Downloading font file {filename}...")
                font_resp = client.get(url)
                font_resp.raise_for_status()
                
                with open(target_font_path, "wb") as font_f:
                    font_f.write(font_resp.content)

                # Replace remote URL with local static URL in CSS
                # FastAPI serves src/salus/static/fonts/ as /static/fonts/
                css_content = css_content.replace(url, f"/static/fonts/{filename}")

            combined_css.append(f"/* --- Font: {name} --- */\n" + css_content)

        except Exception as e:
            print(f"Failed to localize font {name}: {e}")

    # Write combined localized CSS
    fonts_css_target = os.path.join(VENDOR_DIR, "fonts.css")
    with open(fonts_css_target, "w", encoding="utf-8") as out_css:
        out_css.write("\n\n".join(combined_css))
    print(f"\nSaved combined localized stylesheet to {fonts_css_target}")


if __name__ == "__main__":
    main()
