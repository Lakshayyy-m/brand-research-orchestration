import os
from langchain_openai import ChatOpenAI
from langchain_core.messages import SystemMessage, HumanMessage
from dotenv import load_dotenv

from state import XReport

load_dotenv()

llm = ChatOpenAI(
    model="deepseek/deepseek-r1",
    openai_api_key=os.getenv("OPENROUTER_API_KEY"),
    openai_api_base="https://openrouter.ai/api/v1",
)

structured_llm = llm.with_structured_output(XReport)

ANALYSIS_SYSTEM_PROMPT = """You are an X (formerly Twitter) content analysis expert.
You analyse how a brand is being discussed in tweets/posts.
You assess: tone, sentiment, virality signals (views, reposts, quotes, bookmarks),
hashtags, tagged users, and the overall narrative around the brand."""

WRITER_SYSTEM_PROMPT = """You are a senior brand report writer specializing in X/Twitter.
For each post produce:
- A short title summarizing how the brand is discussed
- The post URL
- Bullet points covering tone, sentiment, virality metrics, notable hashtags/tags, and narrative
Pay attention to reposts and quotes — they signal how far the message spread."""


def run_x_crew(x_data: list[dict], brand_name: str) -> XReport:

    analysis_response = llm.invoke(
        [
            SystemMessage(content=ANALYSIS_SYSTEM_PROMPT),
            HumanMessage(content=f"""
    Analyse how '{brand_name}' is being discussed in these X/Twitter posts:

    {x_data}

    For each post cover: URL, views, likes, replies, reposts, quotes, bookmarks,
    hashtags, tagged users, description, original poster, tone and sentiment.
    """),
        ]
    )

    report: XReport = structured_llm.invoke(
        [
            SystemMessage(content=WRITER_SYSTEM_PROMPT),
            HumanMessage(content=f"""
    Using this analysis, write the final structured report for '{brand_name}' on X/Twitter:

    {analysis_response.content}
    """),
        ]
    )

    return report
