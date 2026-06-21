import os
import ssl
import time
import requests
from dotenv import load_dotenv

load_dotenv()

ssl._create_default_https_context = ssl._create_unverified_context


def search_brand(brand_name: str, total_results: int = 15) -> list[dict]:
    """
    Search Google via BrightData SERP proxy.
    Returns the 'organic' results as a list of dicts with 'link', 'title', etc.
    """

    host = "brd.superproxy.io"
    port = 33335

    username = os.getenv("BRIGHT_DATA_USERNAME")
    password = os.getenv("BRIGHT_DATA_PASSWORD")

    proxy_url = f"http://{username}:{password}@{host}:{port}"
    proxies = {"http": proxy_url, "https": proxy_url}

    query = "+".join(brand_name.split())
    url = f"https://www.google.com/search?q=%22{query}%22&tbs=qdr:w&brd_json=1&num={total_results}"

    reponse = requests.get(url, proxies=proxies, verify=False)
    return reponse.json()["organic"]


def scrape_urls(input_urls: list[str], params: dict) -> list[dict]:
    """
    Trigger a BrightData dataset scrape job, poll until ready, return results.
    """

    print(f" Triggering scrape for {len(input_urls)} URLs....")

    api_url = "https://api.brightdata.com/datasets/v3/trigger"

    headers = {
        "Authorization": f"Bearer {os.getenv("BRIGHT_DATA_API")}",
        "Content-Type": "application/json",
    }

    payload = [{"url": u} for u in input_urls]

    trigger_responses = requests.post(
        api_url, headers=headers, params=params, json=payload
    )
    snapshot_id = trigger_responses.json()["snapshot_id"]

    # Poll until results are ready
    tracking_url = f"https://api.brightdata.com/datasets/v3/progress/{snapshot_id}"
    while True:
        status = requests.get(tracking_url, headers=headers).json()["status"]
        if status == "ready":
            break
        print(f" Scrape status: {status} - waiting 10s to recheck...")
        time.sleep(10)

    # Get the fetched data
    output_url = f"https://api.brightdata.com/datasets/v3/snapshot/{snapshot_id}"
    result = requests.get(output_url, headers=headers, params={"format": "json"})
    return result.json()


def route_results(search_results: list[dict]) -> dict[str, list[dict]]:
    """
    Splits raw Google search results into per-platform buckets.
    Returns a dict with keys: linkedin, instagram, youtube, x, web.
    """

    buckets = {"linkedin": [], "instagram": [], "youtube": [], "x": [], "web": []}

    for r in search_results:
        link = r["link"].lower()
        if "linkedin.com" in link:
            buckets["linkedin"].append(r)
        elif "instagram.com" in link:
            buckets["instagram"].append(r)
        elif "youtube.com" in link:
            buckets["youtube"].append(r)
        elif ("x.com" in link or "twitter.com" in link) and "status" in link:
            buckets["x"].append(r)
        else:
            buckets["web"].append(r)

    return buckets
