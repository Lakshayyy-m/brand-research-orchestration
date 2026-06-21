from pydantic import BaseModel, Field
from typing import Optional
from typing_extensions import TypedDict

# Output models


class LinkedInWriterReport(BaseModel):
    post_title: str = Field(
        description="Title explaining how the brand was used in the post"
    )
    post_link: str = Field(description="Link to the scraped post")
    content_lines: list[str] = Field(description="Bullet points relevant to the brand")


class LinkedInReport(BaseModel):
    content: list[LinkedInWriterReport]


class InstagramWriterReport(BaseModel):
    post_title: str = Field(
        description="Title explaining how the brand was used in the post"
    )
    post_link: str = Field(description="Link to the scraped post")
    content_lines: list[str] = Field(description="Bullet points relevant to the brand")


class InstagramReport(BaseModel):
    content: list[InstagramWriterReport]


class YoutubeWriterReport(BaseModel):
    post_title: str = Field(
        description="Title explaining how the brand was used in the video"
    )
    post_link: str = Field(description="Link to the YouTube video")
    content_lines: list[str] = Field(description="Bullet points relevant to the brand")


class YoutubeReport(BaseModel):
    content: list[YoutubeWriterReport]


class XWriterReport(BaseModel):
    post_title: str = Field(
        description="Title explaining how the brand was used in the post"
    )
    post_link: str = Field(description="Link to the scraped post")
    content_lines: list[str] = Field(description="Bullet points relevant to the brand")


class XReport(BaseModel):
    content: list[XWriterReport]


class WebWriterReport(BaseModel):
    post_title: str = Field(
        description="Title explaining how the brand was mentioned on the page"
    )
    post_link: str = Field(description="Link to the scraped page")
    content_lines: list[str] = Field(description="Bullet points relevant to the brand")


class WebReport(BaseModel):
    content: list[WebWriterReport]


# The graph state


class BrandMonitoringState(TypedDict):
    # Inputs
    brand_name: str
    total_results: int

    # Raw search results split by platform
    linkedin_search_response: list[dict]
    instagram_search_response: list[dict]
    youtube_search_response: list[dict]
    x_search_response: list[dict]
    web_search_response: list[dict]

    # Scraped & filtered data per platform
    linkedin_filtered: list[dict]
    instagram_filtered: list[dict]
    youtube_filtered: list[dict]
    x_filtered: list[dict]
    web_filtered: list[dict]

    # Final structured reports
    linkedin_report: Optional[LinkedInReport]
    instagram_report: Optional[InstagramReport]
    youtube_report: Optional[YoutubeReport]
    x_report: Optional[XReport]
    web_report: Optional[WebReport]
