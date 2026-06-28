import streamlit as st
import base64
import gc

from main import run

# Session state initilization
if "response" not in st.session_state:
    st.session_state.response = None

if "deep_seek_image" not in st.session_state:
    st.session_state.deep_seek_image = base64.b64encode(
        open("assets/deep-seek.png", "rb").read()
    ).decode()

if "brightdata_image" not in st.session_state:
    st.session_state.brightdata_image = base64.b64encode(
        open("assets/brightdata_image.png", "rb").read()
    ).decode()


# Callbacks


def reset_analysis():
    st.session_state.response = None
    gc.collect()


def start_analysis():
    status = st.empty()
    status.info(f"Scraping and analysis '{st.session_state.brand_name}'...")

    st.session_state.response = run(
        brand_name=st.session_state.brand_name,
        total_results=st.session_state.total_results,
    )

    status.sucess("Analysis complete!")
    status.empty()


# Side bar

with st.sidebar:
    st.header("Brand Monitoring Settings")

    st.session_state.brandh_name = st.text_input(
        "Company/Brand Name",
        value=(
            "Hugging Face"
            if "brand_name" not in st.session_state
            else st.session_state.brand_name
        ),
    )

    st.session_state.total_results = st.number_input(
        "Total Search Results", min_value=1, max_value=50, value=15, step=1
    )

    st.divider()

    col1, col2 = st.columns(2)

    with col1:
        st.button("Start Analysis", type="primary", on_click=start_analysis)
    with col2:
        st.button("Reset", on_click=reset_analysis)
    

# Header

st.markdown("""
    # Brand Monitoring powered by <img src="data:image/png;base64,{}" width="180" style="vertical-align: -7px;>" & <img src="data:image/png;base64,{}" width="180" style="vertical-align: -10px;">
""".format(st.session_state.deep_seek_image, st.session_state.databright_image))


# Results

if st.session_state.response:
    try:
        r = st.session_state.response
        
        if r.get("linkedin_report"):
            st.markdown("## LinkedIn Mentions")
            for post in r["linkedin_report"].content:
                with st.expander(f"{post.post_title}"):
                    st.markdown(f"**Source:** [{post.post_link}]({post.post_link})")
                    for line in post.content_lines:
                        st.markdown(f"- {line}")
        
        if r.get("instagram_report"):
            st.markdown("## Instagram Mentions")
            for post in r["instagram_report"].content:
                with st.expander(f"{post.post_title}"):
                    st.markdown(f"**Source:** [{post.post_link}]({post.post_link})")
                    for line in post.content_lines:
                        st.markdown(f"- {line}")

        if r.get("youtube_report"):
            st.markdown("## Youtube Mentions")
            for video in r["youtube_report"].content:
                with st.expander(f"{video.video_title}"):
                    st.markdown(f"**Source:** [{video.video_link}]({video.video_link})")
                    for line in video.content_lines:
                        st.markdown(f"- {line}")
        
        if r.get("x_report"):
            st.markdown("## X Mentions")
            for post in r["x_report"].content:
                with st.expander(f"{post.post_title}"):
                    st.markdown(f"**Source:** [{post.post_link}]({post.post_link})")
                    for line in post.content_lines:
                        st.markdown(f"- {line}")
        
        if r.get("web_report"):
            st.markdown("## Web Mentions")
            for post in r["web_report"].content:
                with st.expander(f"{post.post_title}"):
                    st.markdown(f"**Source:** [{post.post_link}]({post.post_link})")
                    for line in post.content_lines:
                        st.markdown(f"- {line}")

    except Exception as e:
        st.error(f"Error displaying results: {e}")

st.markdown("---")
st.markdown("Built with LangGraph, Bright Data and Streamlit")




