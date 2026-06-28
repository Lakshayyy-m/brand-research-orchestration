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

    async def youtube():
        if not state["youtube_search_response"]:
            return
        urls = [r["link"] for r in state["youtube_search_response"]]
        raw = scrape_urls(
            urls, {"dataset_id": "gd_lk56epmy2i5g7lzu0k", "include_errors": "true"}
        )
        filtered = [
            {
                "url": r["url"],
                "title": r["title"],
                "description": r["description"],
                "original_poster": r["youtuber"],
                "verified": r["verified"],
                "hashtags": r["hashtags"],
                "views": r["views"],
                "likes": r["likes"],
                "transcript": r["transcript"],
            }
            for r in raw
        ]

        updates["youtube_filtered"] = filtered
        updates["youtube_report"] = run_youtube_crew(filtered, state["brand_name"])

    async def x():
        if not state["x_search_response"]:
            return
        urls = [r["link"] for r in state["x_search_response"]]
        raw = scrape_urls(
            urls, {"dataset_id": "gd_lwxkxvnf1cynvib9co", "include_errors": "true"}
        )
        filtered = [
            {
                "url": r["url"],
                "views": r["views"],
                "likes": r["likes"],
                "replies": r["replies"],
                "reposts": r["reposts"],
                "original_poster": r["youtuber"],
                "quotes": r["quotes"],
                "bookmarks": r["bookmarks"],
                "hashtags": r["hashtags"],
                "description": r["description"],
                "tagged_users": r["tagged_users"],
            }
            for r in raw
        ]

        updates["x_filtered"] = filtered
        updates["x_report"] = run_x_crew(filtered, state["brand_name"])

    async def web():
        if not state["web_search_response"]:
            return
        urls = [r["link"] for r in state["web_search_response"]]
        raw = scrape_urls(
            urls,
            {
                "dataset_id": "gd_m6gjtfmeh43we6cqc",
                "include_errors": "true",
                "custom_output_fields": "markdown",
            },
        )

        filtered = [
            {
                "url": r["url"],
                "markdown": r["markdown"],
            }
            for r in raw
        ]

        updates["x_filtered"] = filtered
        updates["x_report"] = run_x_crew(filtered, state["brand_name"])

    await asyncio.gather(linkedin(), instagram(), youtube(), x(), web())
    return updates


# Building the graph
def build_graph():
    graph = StateGraph(BrandMonitoringState)

    graph.add_node("search_and_route", search_and_route)
    graph.add_node("scrape_and_analyse", scrape_and_analyse)

    graph.set_entry_point("search_and_route")
    graph.add_edge("search_and_route", "scrape_and_analyse")
    graph.add_edge("scrape_and_analyse")

    return graph.compile()


# Entry point
def run(brand_name: str, total_results: int = 15) -> BrandMonitoringState:
    app = build_graph()
    final_state = app.invoke(
        {
            "brand_name": brand_name,
            "total_results": total_results,
            # Intializing all th list/report fields so LangGraph doesn't complain
            "linkedin_search_response": [],
            "instagram_search_response": [],
            "youtube_search_response": [],
            "x_search_response": [],
            "web_search_response": [],
            "linkedin_filtered": [],
            "instagram_filtered": [],
            "youtube_filtered": [],
            "x_filtered": [],
            "web_filtered": [],
            "linkedin_report": None,
            "instagram_report": None,
            "youtube_report": None,
            "x_report": None,
            "web_report": None,
        }
    )

    return final_state


if __name__ == "__main__":
    result = run("Hugging Face", total_results=15)
