import os
from langchain_openai import ChatOpenAI
from langchain_core.messages import SystemMessage, HumanMessage
from dotenv import load_dotenv

from state import WebReport

load_dotenv()

llm = ChatOpenAI(
    model="deepseek/deepseek-r1",
    openai_api_key=os.getenv("OPENROUTER_API_KEY"),
    openai_api_base="https://openrouter.ai/api/v1",
)

structured_llm = llm.with_structured_output(WebReport)

ANALYSIS_SYSTEM_PROMPT = """You are a web content analysis expert.
You analyse how a brand is being discussed across web pages — blogs, news articles, forums, docs.
You assess: context of mention, tone, sentiment, type of content (review, news, tutorial, etc.),
and the overall narrative the page builds around the brand."""

WRITER_SYSTEM_PROMPT = """You are a senior brand report writer specializing in web content.
For each page produce:
- A short title summarizing how the brand is covered on the page
- The page URL
- Bullet points covering content type, tone, sentiment, key points made about the brand
Focus on what the page is actually *saying* — web content is longer and more nuanced than social posts."""


def run_web_crew(web_data: list[dict], brand_name: str) -> WebReport:

    analysis_response = llm.invoke(
        [
            SystemMessage(content=ANALYSIS_SYSTEM_PROMPT),
            HumanMessage(content=f"""
    Analyse how '{brand_name}' is being discussed on these web pages:

    {web_data}

    Each entry contains the page URL and its full markdown content.
    Identify the type of content, tone, sentiment, and key points made about the brand.
    """),
        ]
    )

    report: WebReport = structured_llm.invoke(
        [
            SystemMessage(content=WRITER_SYSTEM_PROMPT),
            HumanMessage(content=f"""
    Using this analysis, write the final structured report for '{brand_name}' on the web:

    {analysis_response.content}
    """),
        ]
    )

    return report
