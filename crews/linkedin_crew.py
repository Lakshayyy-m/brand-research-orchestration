from langchain_openai import ChatOpenAI
from langchain_core.messages import SystemMessage, HumanMessage
import os
from dotenv import load_dotenv

from state import LinkedInReport

load_dotenv()

llm = ChatOpenAI(
    model="deepseek/deepseek-r1",
    openai_api_key=os.getenv("OPENROUTER_API_KEY"),
    openai_api_base="https://openrouter.ai/api/v1",
)

structured_llm = llm.with_structured_output(LinkedInReport)

ANALYSIS_SYSTEM_PROMPT = """You are a LinkedIn post analytics expert.
You analyse how a brand is being mentioned across LinkedIn posts.
For each post you assess: tone, sentiment, engagement level, paid partnerships, and overall brand perception.
"""
WRITER_SYSTEM_PROMPT = """
You are a senior brand report writer.
You receive a detailed analysis of LinkedIn posts and write a crisp, structured report.
For each post produced:
- A short title summarizing how the brand is used
- The post URL
- Bullet points convering tone, sentiment, engagement, and any notable signals
Keep bullet concise but informative. No fluff.
"""


def run_linkedin_crew(linkedin_data: list[dict], brand_name: str) -> LinkedInReport:
    # Analysis
    analysis_response = llm.invoke(
        [
            SystemMessage(content=ANALYSIS_SYSTEM_PROMPT),
            HumanMessage(content=f"""
    Analyse how '{brand_name}' is being used across these LinkedIn posts:

    {linkedin_data}

    For each post, cover:URL, headline, post test, hashtags, tagged, companies/people, original poster, tone, sentiment, engagement signals, paid partnership (if mentioned).
    """),
        ]
    )

    # Report writing
    report: LinkedInReport = structured_llm.invoke(
        [
            SystemMessage(content=WRITER_SYSTEM_PROMPT),
            HumanMessage(content=f"""
    Using this analysis, write the final structure report for '{brand_name}' on LinkedIn:

    {analysis_response.content}
    """),
        ]
    )

    return report
