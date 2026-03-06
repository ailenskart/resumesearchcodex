import argparse

import requests


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--base-url", default="http://localhost:8000")
    parser.add_argument("--query", required=True)
    parser.add_argument("--limit", type=int, default=5)
    args = parser.parse_args()

    resp = requests.get(f"{args.base_url}/search", params={"q": args.query, "limit": args.limit}, timeout=10)
    resp.raise_for_status()
    data = resp.json()
    for idx, item in enumerate(data["results"], start=1):
        c = item["candidate"]
        print(f"#{idx} {c['name']} | {c['location']} | {c['years_experience']} yrs | score={item['score']}")
        print("  Why:", "; ".join(item["why"]))


if __name__ == "__main__":
    main()
