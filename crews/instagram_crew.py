import os
from langchain_openai import ChatOpenAI
from langchain_core.messages import SystemMessage, HumanMessage
from dotenv import load_dotenv

from state import InstagramReport

load_dotenv()

llm = ChatOpenAI(
    model="deepseek/deepseek-r1",
    openai_api_key=os.getenv("OPENROUTER_API_KEY"),
    openai_api_base="https://openrouter.ai/api/v1",
)

structured_llm = llm.with_structured_output(InstagramReport)

ANALYSIS_SYSTEM_PROMPT = """You are an Instagram content analysis expert.
You analyse how a brand is being mentioned in Instagram posts.
You assess: tone, sentiment, engagement (likes/comments), paid partnerships, 
follower reach, and overall brand perception."""

WRITER_SYSTEM_PROMPT = """You are a senior brand report writer specializing in Instagram.
For each post produce:
- A short title summarizing how the brand is used
- The post URL
- Bullet points covering tone, sentiment, engagement numbers, paid partnership status, and reach
Keep bullets concise but informative."""


def run_instagram_crew(instagram_data: list[dict], brand_name: str) -> InstagramReport:

    analysis_response = llm.invoke(
        [
            SystemMessage(content=ANALYSIS_SYSTEM_PROMPT),
            HumanMessage(content=f"""
    Analyse how '{brand_name}' is being used across these Instagram posts:

    {instagram_data}

    For each post cover: URL, description, likes, comments, paid partnership status,
    follower count, original poster, tone, and sentiment.
    """),
        ]
    )

    report: InstagramReport = structured_llm.invoke(
        [
            SystemMessage(content=WRITER_SYSTEM_PROMPT),
            HumanMessage(content=f"""
    Using this analysis, write the final structured report for '{brand_name}' on Instagram:

    {analysis_response.content}
    """),
        ]
    )

    return report
