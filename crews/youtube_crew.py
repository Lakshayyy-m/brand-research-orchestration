import os
from langchain_openai import ChatOpenAI
from langchain_core.messages import SystemMessage, HumanMessage
from dotenv import load_dotenv

from state import YoutubeReport

load_dotenv()

llm = ChatOpenAI(
    model="deepseek/deepseek-r1",
    openai_api_key=os.getenv("OPENROUTER_API_KEY"),
    openai_api_base="https://openrouter.ai/api/v1",
)

structured_llm = llm.with_structured_output(YoutubeReport)

ANALYSIS_SYSTEM_PROMPT = """You are a YouTube content analysis expert.
You analyse how a brand is mentioned in YouTube videos.
You assess: tone, sentiment, views, likes, verified status, hashtags,
and most importantly — what is said about the brand in the transcript."""

WRITER_SYSTEM_PROMPT = """You are a senior brand report writer specializing in YouTube.
For each video produce:
- A short title summarizing how the brand is covered
- The video URL
- Bullet points covering tone, sentiment, view/like counts, key transcript mentions, and reach
Prioritize what was actually *said* about the brand in the transcript."""


def run_youtube_crew(youtube_data: list[dict], brand_name: str) -> YoutubeReport:

    analysis_response = llm.invoke(
        [
            SystemMessage(content=ANALYSIS_SYSTEM_PROMPT),
            HumanMessage(content=f"""
    Analyse how '{brand_name}' is being covered in these YouTube videos:

    {youtube_data}

    For each video cover: URL, title, description, youtuber, verified status,
    views, likes, hashtags, and what the transcript says about the brand.
    """),
        ]
    )

    report: YoutubeReport = structured_llm.invoke(
        [
            SystemMessage(content=WRITER_SYSTEM_PROMPT),
            HumanMessage(content=f"""
    Using this analysis, write the final structured report for '{brand_name}' on YouTube:

    {analysis_response.content}
    """),
        ]
    )

    return report
