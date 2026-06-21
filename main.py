import asyncio
import os
from dotenv import load_dotenv
from langgraph.graph import StateGraph, END

from state import BrandMonitoringState
from tools.bright_data import search_brand, scrape_urls, route_results
from crews.linkedin_crew import run_linkedin_crew
from crews.instagram_crew import run_instagram_crew
from crews.youtube_crew import run_youtube_crew
from crews.x_crew import run_x_crew
from crews.web_crew import run_web_crew

load_dotenv()


# Node 1 -> Search and route
def search_and_route(state: BrandMonitoringState) -> dict:
    print(f"Searching for '{state['brand_name']}...")

    results = search_brand(state["brand_name"], state["total_results"])
    buckets = route_results(results)

    print(
        f" LinkedIn: {len(buckets['linkedin'])} | "
        f"Instagram: {len(buckets['instagram'])} | "
        f"Youtube: {len(buckets['youtube'])} | "
        f"X: {len(buckets['x'])} | "
        f"Web: {len(buckets['web'])} | "
    )

    return {
        "linkedin_search_response": buckets["linkedin"],
        "instagram_search_response": buckets["instagram"],
        "youtube_search_response": buckets["youtube"],
        "x_search_response": buckets["x"],
        "web_search_response": buckets["web"],
    }


# Node 2 -> Scrape and analyse
async def scrape_and_analyse(state: BrandMonitoringState) -> dict:
    updates = {}

    async def linkedin():
        if not state["linkedin_search_response"]:
            return

        urls = [r["link"] for r in state["linkedin_search_response"]]
        raw = scrape_urls(urls, {"dataset_id": "gd_lyy3tktm25m4avu764"})
        filtered = [
            {
                "url": r["url"],
                "headline": r["headline"],
                "post_text": r["post_text"],
                "hashtags": r["hashtags"],
                "tagged_companies": r["tagged_companies"],
                "tagged_people": r["tagged_people"],
                "original_poster": r["user_id"],
            }
            for r in raw
        ]
        updates["linkedin_filtered"] = filtered
        updates["linkedin_report"] = run_linkedin_crew(filtered, state["brand_name"])

    async def instagram():
        if not state["instagram_search_response"]:
            return

        urls = [r["link"] for r in state["instagram_search_response"]]
        raw = scrape_urls(
            urls, {"dataset_id": "gd_lk5ns7kz21pck8jpis", "include_errors": "true"}
        )
        filtered = [
            {
                "url": r["url"],
                "description": r["description"],
                "likes": r["likes"],
                "num_comments": r["num_comments"],
                "is_paid_partnership": r["is_paid_partnership"],
                "followers": r["followers"],
                "original_poster": r["user_id"],
            }
            for r in raw
        ]
        updates["instagram_filtered"] = filtered
        updates["instagram_report"] = run_instagram_crew(filtered, state["brand_name"])
