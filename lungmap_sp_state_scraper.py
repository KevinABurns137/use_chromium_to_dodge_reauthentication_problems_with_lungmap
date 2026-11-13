#!/usr/bin/env python3

import csv
import json
import os
from pathlib import Path

from playwright.sync_api import sync_playwright

BASE_LOGIN_URL = "https://ingest.lungmap.net/"
CSV_FILE = "curlsToMake.csv"
STATE_FILE = "sp_storage_state.json"
OUTPUT_DIR = "output"

Path(OUTPUT_DIR).mkdir(exist_ok=True)


def create_state():
    """
    Interactive login and save state.
    Run this once if sp_storage_state.json doesn't exist.
    """
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)

        context = browser.new_context()

        page = context.new_page()

        print(f"Opening {BASE_LOGIN_URL}")
        page.goto(BASE_LOGIN_URL, wait_until="networkidle", timeout=120000)

        input(
            "\nLog in completely.\n"
            "When you can manually browse ingest.lungmap.net successfully,\n"
            "press ENTER here.\n"
        )

        context.storage_state(path=STATE_FILE)

        print(f"Saved {STATE_FILE}")

        browser.close()


def load_rows():
    with open(CSV_FILE, newline="", encoding="utf-8") as f:
        return list(csv.DictReader(f))


def fetch_json(context, url):
    """
    Execute request from authenticated browser context.
    """

    response = context.request.get(url)

    print(
        f"{response.status} "
        f"{url}"
    )

    body = response.text()

    try:
        return json.loads(body)
    except Exception:
        return {
            "_status": response.status,
            "_content_type": response.headers.get("content-type"),
            "_raw_text": body,
        }


def main():

    if not os.path.exists(STATE_FILE):
        create_state()

    rows = load_rows()

    with sync_playwright() as p:

        browser = p.chromium.launch(headless=True)

        context = browser.new_context(
            storage_state=STATE_FILE
        )

        total = 0

        for row in rows:

            uid = row["uid"].strip()

            jobs = [
                ("edges", row["edges"].strip() + uid),
                ("non-schema", row["non-schema"].strip() + uid),
                ("form", row["form"].strip() + uid),
            ]

            for label, url in jobs:

                print(f"\n[{label}] {uid}")

                data = fetch_json(context, url)

                outfile = os.path.join(
                    OUTPUT_DIR,
                    f"{uid}_{label}.json"
                )

                with open(
                    outfile,
                    "w",
                    encoding="utf-8"
                ) as out:

                    json.dump(
                        data,
                        out,
                        indent=2,
                        ensure_ascii=False
                    )

                total += 1

        browser.close()

    print()
    print(f"Created {total} files")
    print(f"Expected: {len(rows) * 3}")


if __name__ == "__main__":
    main()