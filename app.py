import streamlit as st
import pandas as pd
from datetime import datetime
import json
import html
from typing import Optional
from logger import get_logger
from concern_risk_misc_naics import concerns_events, emerging_risks, misc_topics, naics_data
import streamlit.components.v1 as components
import requests
import asyncio
import yaml
with open('config.yaml', 'r') as file:
    config = yaml.safe_load(file)

import os
from dotenv import load_dotenv

load_dotenv()

logger = get_logger(__name__)


# Page configuration
st.set_page_config(
    page_title="Emerging Insights Query System",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Enhanced CSS for card-based layout
st.markdown("""
<style>
    /* Global font consistency - apply to main content areas */
    .main, .block-container, .stMarkdown, p, div, span, h1, h2, h3, h4, h5, h6 {
        font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', 'Roboto', 'Helvetica', 'Arial', sans-serif;
    }
    /* Reduce overall UI element sizes */
    button[data-baseweb="button"] {
        font-size: 0.85rem !important;
        padding: 0.4rem 0.8rem !important;
        min-height: 32px !important;
    }
    /* Reduce heading sizes */
    h1 { font-size: 1.8rem !important; }
    h2 { font-size: 1.4rem !important; }
    h3 { font-size: 1.1rem !important; }
    /* Reduce spacing in filter section */
    .filter-section h3 {
        font-size: 1.0rem !important;
        margin-bottom: 10px !important;
    }
    /* Make text black by default, only actual links blue */
    p, div, span, h1, h2, h3, h4, h5, h6, strong, b {
        color: #000000 !important;
    }
    /* Only actual clickable links should be blue */
    a[href]:not([href="#"]):not([href^="javascript:"]) {
        color: #1f77b4 !important;
        text-decoration: underline;
    }
    a[href]:not([href="#"]):not([href^="javascript:"]):hover {
        color: #0d5a87 !important;
    }
    /* Non-link text should be black */
    a[href="#"], a[href^="javascript:"] {
        color: #000000 !important;
        text-decoration: underline;
    }
    /* Streamlit markdown - headings and labels should be black */
    .stMarkdown h1, .stMarkdown h2, .stMarkdown h3, .stMarkdown h4, .stMarkdown h5, .stMarkdown h6 {
        color: #000000 !important;
    }
    /* Document metadata - labels should be black */
    .document-metadata strong {
        color: #000000 !important;
    }
    /* Show more/less button styling - make it look like a black link */
    button[data-testid*="summary_btn"] {
        color: #000000 !important;
        background: none !important;
        border: none !important;
        text-decoration: underline !important;
        padding: 0 !important;
        font-size: inherit !important;
        cursor: pointer !important;
        box-shadow: none !important;
        font-weight: normal !important;
    }
    /* Enhanced tab styling - make numbers visible and eye-catching */
    .stTabs [data-baseweb="tab-list"] {
        gap: 6px;
        background-color: #f8f9fa;
        padding: 10px;
        border-radius: 8px 8px 0 0;
        border-bottom: 2px solid #dee2e6;
    }
    .stTabs [data-baseweb="tab"] {
        background-color: #ffffff;
        border: 1px solid #dee2e6;
        border-bottom: none;
        border-radius: 8px 8px 0 0;
        padding: 12px 18px;
        font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', 'Roboto', 'Helvetica', 'Arial', sans-serif;
        font-size: 0.9rem;
        font-weight: 500;
        color: #495057;
        transition: all 0.2s ease;
        text-align: left !important;
        overflow: visible !important;
        text-overflow: clip !important;
        white-space: nowrap !important;
        min-width: fit-content;
        position: relative;
    }
    .stTabs [data-baseweb="tab"]::before {
        content: '';
        position: absolute;
        left: 0;
        top: 0;
        bottom: 0;
        width: 3px;
        background-color: #1f77b4;
        border-radius: 8px 0 0 0;
        opacity: 0;
        transition: opacity 0.2s;
    }
    .stTabs [data-baseweb="tab"]:hover {
        background-color: #f0f7ff;
        color: #1f77b4;
        border-color: #1f77b4;
        transform: translateY(-2px);
        box-shadow: 0 2px 8px rgba(31, 119, 180, 0.15);
    }
    .stTabs [data-baseweb="tab"]:hover::before {
        opacity: 1;
    }
    .stTabs [aria-selected="true"] {
        background-color: #ffffff;
        color: #1f77b4;
        font-weight: 600;
        border-color: #1f77b4;
        border-bottom: 2px solid #ffffff;
        margin-bottom: -2px;
        box-shadow: 0 -2px 8px rgba(31, 119, 180, 0.1);
    }
    .stTabs [aria-selected="true"]::before {
        opacity: 1;
    }
    .stTabs [data-baseweb="tab"] > div {
        overflow: visible !important;
    }
    .main-header {
        font-size: 1.8rem;
        color: #1f77b4;
        text-align: center;
        margin-bottom: 0.5rem;
        font-weight: bold;
        font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', 'Roboto', 'Helvetica', 'Arial', sans-serif;
    }
    .sub-header {
        font-size: 0.95rem;
        color: #555;
        text-align: center;
        margin-bottom: 1rem;
    }
    .stats-box {
        background-color: #f0f2f6;
        padding: 3px 8px;
        border-radius: 4px;
        border-left: 2px solid #1f77b4;
        margin: 1px 0;
        height: 30px;
        max-height: 30px;
        display: flex;
        flex-direction: row;
        justify-content: space-between;
        align-items: center;
        overflow: hidden;
        box-sizing: border-box;
        width: 100%;
    }
    .stats-box h2 {
        font-size: 0.65rem;
        margin: 0;
        font-weight: 600;
        line-height: 1.0;
        white-space: nowrap;
        overflow: hidden;
        text-overflow: ellipsis;
        flex-shrink: 1;
        min-width: 0;
        padding-right: 8px;
        color: #495057;
    }
    .stats-box h3 {
        font-size: 0.85rem;
        margin: 0;
        font-weight: 700;
        line-height: 1.0;
        white-space: nowrap;
        flex-shrink: 0;
        text-align: right;
        color: #1f77b4;
    }
    .query-explanation {
        background-color: #e8f4f8;
        padding: 15px;
        border-radius: 8px;
        border-left: 4px solid #2196F3;
        margin: 15px 0;
        font-size: 0.9rem;
    }
    /* Make expanders smaller */
    div[data-testid="stExpander"] {
        margin: 5px 0 !important;
    }
    div[data-testid="stExpander"] > div {
        padding: 4px 8px !important;
    }
    div[data-testid="stExpander"] summary {
        font-size: 0.75rem !important;
        padding: 4px 8px !important;
        min-height: 28px !important;
        line-height: 1.2 !important;
    }
    div[data-testid="stExpander"] summary > div {
        font-size: 0.75rem !important;
    }
    div[data-testid="stExpander"] > div[data-testid="stExpanderDetails"] {
        padding: 8px 12px !important;
        font-size: 0.75rem !important;
    }
    /* Make JSON content in expanders smaller */
    div[data-testid="stExpander"] pre {
        font-size: 0.7rem !important;
        padding: 8px !important;
        margin: 4px 0 !important;
    }
    div[data-testid="stExpander"] code {
        font-size: 0.7rem !important;
    }
    .article-card {
        background: white;
        border: 1px solid #e0e0e0;
        border-radius: 12px;
        padding: 20px;
        margin-bottom: 20px;
        box-shadow: 0 2px 8px rgba(0,0,0,0.1);
        transition: all 0.3s ease;
    }
    .article-card:hover {
        box-shadow: 0 4px 16px rgba(0,0,0,0.15);
        transform: translateY(-2px);
    }
    .article-title {
        font-size: 1.3rem;
        font-weight: bold;
        color: #1f77b4;
        margin-bottom: 10px;
        line-height: 1.4;
    }
    .article-summary {
        color: #555;
        font-size: 0.95rem;
        line-height: 1.6;
        margin-bottom: 15px;
        font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', 'Roboto', 'Helvetica', 'Arial', sans-serif;
    }
    .article-meta {
        display: flex;
        gap: 15px;
        flex-wrap: wrap;
        margin-bottom: 10px;
        font-size: 0.85rem;
    }
    .meta-item {
        background: #f5f5f5;
        padding: 5px 10px;
        border-radius: 5px;
        color: #666;
    }
    .tag-current {
        background-color: #4CAF50;
        color: white;
        padding: 5px 12px;
        border-radius: 5px;
        font-weight: bold;
        display: inline-block;
    }
    .tag-trend {
        background-color: #FF9800;
        color: white;
        padding: 5px 12px;
        border-radius: 5px;
        font-weight: bold;
        display: inline-block;
    }
    .tag-untagged {
        background-color: #9E9E9E;
        color: white;
        padding: 5px 12px;
        border-radius: 5px;
        font-weight: bold;
        display: inline-block;
    }
    .tag-error {
        background-color: #F44336;
        color: white;
        padding: 5px 12px;
        border-radius: 5px;
        font-weight: bold;
        display: inline-block;
    }
    .expand-btn {
        background-color: #1f77b4;
        color: white;
        border: none;
        padding: 8px 16px;
        border-radius: 5px;
        cursor: pointer;
        font-size: 0.9rem;
        transition: background-color 0.3s;
    }
    .expand-btn:hover {
        background-color: #155a8a;
    }
    .full-content {
        background: #f9f9f9;
        padding: 20px;
        border-radius: 8px;
        margin-top: 15px;
        border-left: 4px solid #1f77b4;
    }
    .filter-section {
        background: #f8f9fa;
        padding: 12px 16px;
        border-radius: 8px;
        margin-bottom: 15px;
        margin-top: 0 !important;
    }
    /* Reduce spacing around horizontal rules (separators) */
    hr {
        margin: 5px 0 !important;
        border: none;
        border-top: 1px solid #e0e0e0;
    }
    /* Reduce spacing before filter section */
    .stMarkdown:has(hr) + div .filter-section,
    .stMarkdown:has(hr) ~ div .filter-section {
        margin-top: 5px !important;
    }
    /* Reduce spacing after statistics columns */
    div[data-testid="column"]:has(.stats-box) {
        margin-bottom: 0 !important;
        padding-bottom: 0 !important;
    }
    /* Eliminate extra gray space below statistics section */
    div[data-testid="column"]:has(.stats-box) .element-container {
        margin-bottom: 0 !important;
        padding-bottom: 0 !important;
    }
    /* Remove spacing from the row container holding stats columns */
    div[data-testid="stHorizontalBlock"]:has(div[data-testid="column"]:has(.stats-box)) {
        margin-bottom: 0 !important;
        padding-bottom: 0 !important;
    }
    /* Remove spacing from markdown containers in stats columns */
    div[data-testid="column"]:has(.stats-box) .stMarkdown {
        margin-bottom: 0 !important;
        padding-bottom: 0 !important;
    }
    /* Remove spacing from the container that wraps the stats row */
    div[data-testid="stHorizontalBlock"]:has(div[data-testid="column"]:has(.stats-box)) .element-container {
        margin-bottom: 0 !important;
        padding-bottom: 0 !important;
    }
    /* Target the immediate parent of stats columns to remove spacing */
    div[data-testid="column"]:has(.stats-box) > div {
        margin-bottom: 0 !important;
        padding-bottom: 0 !important;
    }
    /* Remove spacing after the stats row - target next sibling */
    div[data-testid="stHorizontalBlock"]:has(div[data-testid="column"]:has(.stats-box)) + div,
    div[data-testid="stHorizontalBlock"]:has(div[data-testid="column"]:has(.stats-box)) ~ div {
        margin-top: 0 !important;
        padding-top: 0 !important;
    }
    /* Remove all spacing from block container that holds stats */
    .block-container:has(div[data-testid="stHorizontalBlock"]:has(div[data-testid="column"]:has(.stats-box))) {
        padding-bottom: 0 !important;
    }
    /* Remove spacing from main container when stats are present */
    .main .block-container:has(div[data-testid="stHorizontalBlock"]:has(div[data-testid="column"]:has(.stats-box))) {
        padding-bottom: 0 !important;
    }
    /* Target the element container that wraps stats horizontal block */
    div[data-testid="element-container"]:has(div[data-testid="stHorizontalBlock"]:has(div[data-testid="column"]:has(.stats-box))) {
        margin-bottom: 0 !important;
        padding-bottom: 0 !important;
    }
    /* Aggressive removal of spacing after stats - use negative margin if needed */
    div[data-testid="stHorizontalBlock"]:has(div[data-testid="column"]:has(.stats-box)) {
        margin-bottom: -1rem !important;
    }
    /* Remove spacing from the element container immediately after stats */
    div[data-testid="stHorizontalBlock"]:has(div[data-testid="column"]:has(.stats-box)) + div[data-testid="element-container"] {
        margin-top: -1rem !important;
        padding-top: 0 !important;
    }
    /* Target the filter section container to remove top spacing */
    div[data-testid="element-container"]:has(.filter-section) {
        margin-top: 0 !important;
        padding-top: 0 !important;
    }
    /* Remove spacing between stats and filter section - target all intermediate containers */
    div[data-testid="stHorizontalBlock"]:has(div[data-testid="column"]:has(.stats-box)) ~ div[data-testid="element-container"]:has(.filter-section) {
        margin-top: -2rem !important;
        padding-top: 0 !important;
    }
    /* Target ALL element containers between stats and filters - very aggressive */
    div[data-testid="element-container"]:has(div[data-testid="stHorizontalBlock"]:has(div[data-testid="column"]:has(.stats-box))) + div[data-testid="element-container"],
    div[data-testid="element-container"]:has(div[data-testid="stHorizontalBlock"]:has(div[data-testid="column"]:has(.stats-box))) ~ div[data-testid="element-container"] {
        margin-top: -3rem !important;
        padding-top: 0 !important;
    }
    /* Remove all spacing from block container when it contains stats followed by filters */
    .block-container:has(div[data-testid="stHorizontalBlock"]:has(div[data-testid="column"]:has(.stats-box))):has(div[data-testid="element-container"]:has(.filter-section)) {
        padding: 0 !important;
    }
    /* Hide empty element containers that might be causing gray space */
    div[data-testid="element-container"]:empty,
    div[data-testid="element-container"]:has(> div:empty) {
        display: none !important;
        height: 0 !important;
        margin: 0 !important;
        padding: 0 !important;
    }
    /* Remove background from empty containers between stats and filters */
    div[data-testid="element-container"]:has(div[data-testid="stHorizontalBlock"]:has(div[data-testid="column"]:has(.stats-box))) ~ div[data-testid="element-container"]:not(:has(.filter-section)):not(:has(*)) {
        display: none !important;
    }
    /* Reduce spacing in markdown containers that contain separators */
    .stMarkdown:has(hr) {
        margin-bottom: 0.5rem !important;
        margin-top: 0.5rem !important;
    }
    /* Fix dropdown text size and padding - ensure text fits inside boxes */
    div[data-baseweb="select"] > div {
        font-size: 0.7rem !important;
        padding: 3px 6px !important;
        min-height: 30px !important;
        max-height: 30px !important;
        line-height: 1.1 !important;
        display: flex !important;
        align-items: center !important;
        box-sizing: border-box !important;
    }
    div[data-baseweb="select"] input {
        font-size: 0.7rem !important;
        padding: 2px 4px !important;
        line-height: 1.1 !important;
        height: auto !important;
    }
    /* Fix multiselect dropdown - tags and source filters */
    div[data-baseweb="popover"] {
        font-size: 0.7rem !important;
    }
    div[data-baseweb="popover"] li {
        font-size: 0.7rem !important;
        padding: 3px 8px !important;
        line-height: 1.2 !important;
    }
    /* Ensure text fits in selectbox - prevent overflow */
    div[data-baseweb="select"] > div > div {
        overflow: hidden !important;
        text-overflow: ellipsis !important;
        white-space: nowrap !important;
        max-width: 100% !important;
        padding: 0 2px !important;
        font-size: 0.7rem !important;
        line-height: 1.1 !important;
    }
    /* Fix multiselect value display - tags inside the box */
    div[data-baseweb="select"] span[data-baseweb="tag"] {
        font-size: 0.65rem !important;
        padding: 2px 4px !important;
        margin: 1px 2px !important;
        line-height: 1.1 !important;
        max-width: 100% !important;
        overflow: hidden !important;
        text-overflow: ellipsis !important;
        white-space: nowrap !important;
    }
    /* Fix placeholder text in multiselect */
    div[data-baseweb="select"] div[data-baseweb="placeholder"] {
        font-size: 0.7rem !important;
        padding: 0 2px !important;
        line-height: 1.1 !important;
    }
    /* Fix label text size for filter section */
    .filter-section label[data-testid="stWidgetLabel"] {
        font-size: 0.8rem !important;
        margin-bottom: 3px !important;
        font-weight: 500 !important;
    }
    /* Ensure filter section dropdowns have consistent sizing */
    .filter-section div[data-baseweb="select"] {
        min-width: 100% !important;
    }
    .filter-section div[data-baseweb="select"] > div {
        width: 100% !important;
        box-sizing: border-box !important;
    }
    /* Fix multiselect selected items display */
    div[data-baseweb="select"] span {
        font-size: 0.65rem !important;
        padding: 2px 4px !important;
        line-height: 1.1 !important;
        max-width: 100% !important;
        overflow: hidden !important;
        text-overflow: ellipsis !important;
        white-space: nowrap !important;
    }
    /* Ensure placeholder text fits */
    div[data-baseweb="select"] input::placeholder {
        font-size: 0.7rem !important;
        color: #666 !important;
    }
    .concern-badge {
        background: #e3f2fd;
        color: #1976d2;
        padding: 4px 10px;
        border-radius: 4px;
        margin: 3px;
        display: inline-block;
        font-size: 0.85rem;
    }
    .misc-badge {
        background: #ede7f6;
        color: #512da8;
        padding: 4px 10px;
        border-radius: 4px;
        margin: 3px;
        display: inline-block;
        font-size: 0.85rem;
    }
    .risks-badge {
        background: #fce4ec;
        color: #ad1457;
        padding: 4px 10px;
        border-radius: 4px;
        margin: 3px;
        display: inline-block;
        font-size: 0.85rem;
    }
    .naics-section {
        margin-top: 5px;
    }

    .naics-badge {
        background: #fff3e0;
        color: #f57c00;
        padding: 4px 10px;
        border-radius: 4px;
        margin: 3px;
        display: inline-block;
        font-size: 0.85rem;
    }

    .naics-desc {
        background: #f1f8e9;
        color: #33691e;
        padding: 4px 10px;
        border-radius: 4px;
        margin: 3px;
        display: inline-block;
        font-size: 0.85rem;
    }

    /* Target the expander summary text */
    div > div[data-testid="stMarkdownContainer"] > p {
        color: #1E90FF;      /* Your desired color */
        font-size: 18px;      /* Your desired font size */
    }

    /* Optional: change hover color for expander header */
    div > div[data-testid="stMarkdownContainer"] > p:hover {
        color: #2832C0;
    }
    /* Fix radio button wrapping - keep CourtListener on same line */
    div[data-testid="stRadio"] > div {
        flex-wrap: nowrap !important;
        display: flex !important;
    }
    div[data-testid="stRadio"] label {
        white-space: nowrap !important;
        margin-right: 25px !important;
        flex-shrink: 0 !important;
    }
    /* CourtListener Docket Card Styling */
    .docket-card {
        background: linear-gradient(135deg, #f8f9fa 0%, #ffffff 100%);
        border: 2px solid #e0e0e0;
        border-left: 5px solid #1f77b4;
        border-radius: 12px;
        padding: 20px;
        margin-bottom: 20px;
        box-shadow: 0 2px 8px rgba(0,0,0,0.08);
        transition: all 0.3s ease;
        font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', 'Roboto', 'Helvetica', 'Arial', sans-serif;
    }
    .docket-card:hover {
        box-shadow: 0 4px 16px rgba(0,0,0,0.12);
        transform: translateY(-2px);
        border-left-color: #4CAF50;
    }
    .docket-header {
        font-size: 1.1rem;
        font-weight: 600;
        color: #1f77b4;
        margin-bottom: 12px;
        line-height: 1.4;
        word-wrap: break-word;
        overflow-wrap: break-word;
        font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', 'Roboto', 'Helvetica', 'Arial', sans-serif;
    }
    .docket-meta-grid {
        display: flex;
        flex-wrap: wrap;
        gap: 8px;
        margin-top: 15px;
        align-items: center;
        width: 100%;
    }
    .docket-meta-item {
        background: #f5f7fa;
        padding: 6px 10px;
        border-radius: 6px;
        border-left: 3px solid #1f77b4;
        font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', 'Roboto', 'Helvetica', 'Arial', sans-serif;
        display: inline-flex;
        align-items: center;
        gap: 6px;
        white-space: nowrap;
        margin: 0;
        flex-shrink: 0;
        flex-grow: 0;
    }
    .docket-meta-label {
        font-size: 0.8rem;
        color: #666;
        text-transform: uppercase;
        letter-spacing: 0.5px;
        font-weight: 600;
        font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', 'Roboto', 'Helvetica', 'Arial', sans-serif;
        margin: 0;
    }
    .docket-meta-value {
        font-size: 0.8rem;
        color: #333;
        font-weight: 500;
        font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', 'Roboto', 'Helvetica', 'Arial', sans-serif;
        margin: 0;
        white-space: nowrap;
    }
    .document-card {
        background: #ffffff;
        border: 1px solid #e0e0e0;
        border-radius: 8px;
        padding: 15px;
        margin: 10px 0;
        border-left: 3px solid #4CAF50;
        font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', 'Roboto', 'Helvetica', 'Arial', sans-serif;
    }
    .document-card:hover {
        border-left-color: #1f77b4;
        box-shadow: 0 2px 6px rgba(0,0,0,0.1);
    }
    /* Improve tab styling for documents */
    .stTabs [data-baseweb="tab-list"] {
        gap: 4px;
        background-color: #f8f9fa;
        padding: 8px;
        border-radius: 8px 8px 0 0;
    }
    .stTabs [data-baseweb="tab"] {
        background-color: #ffffff;
        border: 1px solid #dee2e6;
        border-bottom: none;
        border-radius: 8px 8px 0 0;
        padding: 10px 16px;
        font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', 'Roboto', 'Helvetica', 'Arial', sans-serif;
        font-size: 0.9rem;
        font-weight: 500;
        color: #495057;
        transition: all 0.2s ease;
    }
    .stTabs [data-baseweb="tab"]:hover {
        background-color: #f8f9fa;
        color: #1f77b4;
    }
    .stTabs [aria-selected="true"] {
        background-color: #ffffff;
        color: #1f77b4;
        font-weight: 600;
        border-bottom: 2px solid #ffffff;
        margin-bottom: -2px;
        box-shadow: 0 -2px 4px rgba(0,0,0,0.05);
    }
    /* Document metadata styling */
    .document-metadata {
        font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', 'Roboto', 'Helvetica', 'Arial', sans-serif;
        font-size: 0.95rem;
        color: #333;
        line-height: 1.6;
    }
    .document-metadata strong {
        color: #1f77b4;
        font-weight: 600;
    }
    .selectable-content {
        background-color: #f8f9fa;
        border: 1px solid #dee2e6;
        border-radius: 6px;
        padding: 15px;
        max-height: 400px;
        overflow-y: auto;
        font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', 'Roboto', 'Helvetica', 'Arial', sans-serif;
        font-size: 0.95rem;
        line-height: 1.6;
        white-space: pre-wrap;
        word-wrap: break-word;
        user-select: text;
        -webkit-user-select: text;
        -moz-user-select: text;
        -ms-user-select: text;
        cursor: text;
        color: #333;
    }
    .selectable-content::-webkit-scrollbar {
        width: 8px;
    }
    .selectable-content::-webkit-scrollbar-track {
        background: #f1f1f1;
        border-radius: 4px;
    }
    .selectable-content::-webkit-scrollbar-thumb {
        background: #888;
        border-radius: 4px;
    }
    .selectable-content::-webkit-scrollbar-thumb:hover {
        background: #555;
    }
    /* Collapsible scrollable summary */
    .summary-container {
        margin: 10px 0;
    }
    .summary-preview {
        color: #333;
        font-size: 0.95rem;
        line-height: 1.6;
        margin-bottom: 8px;
    }
    .summary-full {
        color: #333;
        font-size: 0.95rem;
        line-height: 1.6;
        max-height: 300px;
        overflow-y: auto;
        padding: 10px;
        background-color: #f8f9fa;
        border: 1px solid #dee2e6;
        border-radius: 6px;
        margin-bottom: 8px;
    }
    .summary-full::-webkit-scrollbar {
        width: 8px;
    }
    .summary-full::-webkit-scrollbar-track {
        background: #f1f1f1;
        border-radius: 4px;
    }
    .summary-full::-webkit-scrollbar-thumb {
        background: #888;
        border-radius: 4px;
    }
    .summary-full::-webkit-scrollbar-thumb:hover {
        background: #555;
    }
    .summary-toggle-btn {
        color: #000000 !important;
        background: none !important;
        border: none !important;
        text-decoration: underline !important;
        padding: 0 !important;
        font-size: inherit !important;
        cursor: pointer !important;
        box-shadow: none !important;
        font-weight: normal !important;
        font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', 'Roboto', 'Helvetica', 'Arial', sans-serif;
    }
    .summary-toggle-btn:hover {
        color: #333333 !important;
    }
</style>
""", unsafe_allow_html=True)


class InsuranceQueryApp:
    def __init__(self):
        self.initialize_session_state()
        # self.dynamo_client = DynamoDBClient()
        # self.query_generator = OpenSearchQueryGenerator()

        # self.os_client = OpenSearchIndexManager()
        self.index_name = "ei_articles_index-05-nov-test"  # replace with your actual index

    def initialize_session_state(self):
        """Initialize session state variables."""
        if 'query_results' not in st.session_state:
            st.session_state.query_results = None
        if 'query_history' not in st.session_state:
            st.session_state.query_history = []
        if 'last_query' not in st.session_state:
            st.session_state.last_query = ""
        if 'expanded_articles' not in st.session_state:
            st.session_state.expanded_articles = set()
        if 'last_source_filter' not in st.session_state:
            st.session_state.last_source_filter = None
        if 'expanded_dockets' not in st.session_state:
            st.session_state.expanded_dockets = set()

    def format_tag(self, tag: str) -> str:
        """Format tag with appropriate styling."""
        if not tag:
            return '<span class="tag-untagged">Untagged</span>'
        
        tag_classes = {
            "Current": "tag-current",
            "Potential New Trend": "tag-trend",
            "Untagged": "tag-untagged",
            "Processing Error": "tag-error"
        }
        
        css_class = tag_classes.get(tag, "tag-untagged")
        return f'<span class="{css_class}">{tag}</span>'
    
    def clean_document_title(self, title: str) -> str:
        """Remove related document references, author info, and 'Ordered by' text from title."""
        import re
        if not title:
            return title
        
        # Remove patterns like "(related document(s)[23][209][39][20])" or "(related document(s) [23][209])"
        # Pattern matches: (related document(s) followed by brackets with numbers, then closing paren)
        cleaned = re.sub(r'\s*\(related document\(s\)\s*\[[^\]]*\](?:\s*\[[^\]]*\])*\)\.?\s*', '', title, flags=re.IGNORECASE)
        # Also handle cases without brackets: (related document(s))
        cleaned = re.sub(r'\s*\(related document\(s\)\)\.?\s*', '', cleaned, flags=re.IGNORECASE)
        # Remove "(Related Doc [21])" pattern
        cleaned = re.sub(r'\s*\([Rr]elated [Dd]oc\s*\[[^\]]*\]\)\.?\s*', '', cleaned)
        # Remove "No. of Notices: X. Notice Date..." pattern
        cleaned = re.sub(r'\s*No\.\s*of\s*Notices:\s*\d+\.\s*Notice\s*Date\s*[^\s]+.*$', '', cleaned, flags=re.IGNORECASE)
        # Remove patterns like "(related document(s) (Related Doc [21]))"
        cleaned = re.sub(r'\s*\(related document\(s\)\s*\([Rr]elated [Dd]oc\s*\[[^\]]*\]\)\)\.?\s*', '', cleaned, flags=re.IGNORECASE)
        
        # Remove "Ordered by..." text and everything after it
        cleaned = re.sub(r'\s*[Oo]rdered by.*$', '', cleaned)
        cleaned = re.sub(r'\s*[Ss]igned by.*$', '', cleaned)
        
        # Remove author info like "(D., Tasha)" or similar at the end (but keep if it's part of the main title)
        # Only remove if it's at the very end and looks like author info
        cleaned = re.sub(r'\s*\([^)]*\)\.?\s*$', '', cleaned)
        
        # Remove "PACER Document" text (case insensitive, anywhere in the title)
        # Handle variations: "PACER Document", "PACERDocument", "pacer document", "PACER Document.", etc.
        # Match with optional spaces, punctuation, and before/after
        cleaned = re.sub(r'\s*PACER\s*Document\s*\.?\s*', ' ', cleaned, flags=re.IGNORECASE)
        cleaned = re.sub(r'\s*PACER\s*Document\s*$', '', cleaned, flags=re.IGNORECASE)  # Remove if at end
        cleaned = re.sub(r'^\s*PACER\s*Document\s*', '', cleaned, flags=re.IGNORECASE)  # Remove if at start
        
        # Clean up any double spaces or trailing periods that might result
        cleaned = re.sub(r'\s+', ' ', cleaned).strip()
        cleaned = cleaned.rstrip('.')
        return cleaned
    
    def group_courtlistener_by_docket(self, results: list) -> dict:
        """Group CourtListener documents by docket_id."""
        dockets = {}
        
        for doc in results:
            # Extract source_meta - handle both dict and string formats
            source_meta_raw = doc.get('source_meta', {})
            source_meta = {}
            
            # Handle different source_meta formats
            if isinstance(source_meta_raw, str):
                try:
                    source_meta = json.loads(source_meta_raw)
                except json.JSONDecodeError:
                    # Try to parse if it's a string representation of dict
                    try:
                        import ast
                        source_meta = ast.literal_eval(source_meta_raw)
                    except:
                        source_meta = {}
            elif isinstance(source_meta_raw, dict):
                source_meta = source_meta_raw
            else:
                source_meta = {}
            
            # If source_meta is empty but doc has the fields at top level, use doc directly
            # This handles cases where OpenSearch might have flattened the structure
            if not source_meta or (isinstance(source_meta, dict) and len(source_meta) == 0):
                # Check if metadata fields exist at document top level
                if any(key in doc for key in ['case_name', 'caseName', 'docket_id', 'docketId', 'court']):
                    source_meta = doc
            
            # Extract docket_id - try multiple field name variations
            docket_id = (source_meta.get('docket_id') or 
                        source_meta.get('docketId') or
                        source_meta.get('docket_ID'))
            
            if not docket_id:
                # If no docket_id, treat as standalone document
                docket_id = f"standalone_{doc.get('url', 'unknown')}"
            
            # Only create docket entry if we haven't seen this docket_id before
            if docket_id not in dockets:
                # Extract all metadata fields - try multiple naming conventions
                case_name = (source_meta.get('case_name') or 
                           source_meta.get('caseName') or
                           source_meta.get('CaseName') or
                           'Unknown Case')
                
                court = (source_meta.get('court') or 
                        source_meta.get('Court') or
                        'Unknown Court')
                
                date_filed = (source_meta.get('date_filed') or 
                             source_meta.get('dateFiled') or
                             source_meta.get('DateFiled') or
                             '')
                
                docket_number = (source_meta.get('docket_number') or 
                               source_meta.get('docketNumber') or
                               source_meta.get('DocketNumber') or
                               '')
                
                assigned_to = (source_meta.get('assigned_to') or 
                              source_meta.get('assignedTo') or
                              source_meta.get('AssignedTo') or
                              '')
                
                cause = (source_meta.get('cause') or 
                        source_meta.get('Cause') or
                        '')
                
                dockets[docket_id] = {
                    'docket_id': str(docket_id),
                    'case_name': case_name,
                    'court': court,
                    'date_filed': date_filed,
                    'docket_number': docket_number,
                    'assigned_to': assigned_to,
                    'cause': cause,
                    'documents': []
                }
            
            dockets[docket_id]['documents'].append(doc)
        
        return dockets
    
    def render_courtlistener_docket(self, docket_info: dict, docket_key: str):
        """Render a CourtListener docket with its documents."""
        case_name = docket_info['case_name']
        docket_number = docket_info['docket_number']
        court = docket_info['court']
        date_filed = docket_info['date_filed']
        num_docs = len(docket_info['documents'])
        
        # Truncate long case names for better UI
        display_case_name = case_name
        if len(case_name) > 80:
            display_case_name = case_name[:77] + "..."
        
        # Create docket header with better formatting
        docket_title = f"⚖️ {display_case_name}"
        if docket_number:
            docket_title += f" • {docket_number}"
        
        # Use a container for better styling
        with st.container():
            # Track expander state to preserve after rerun
            docket_expander_key = f"docket_exp_{docket_key}"
            is_expanded = docket_expander_key in st.session_state.expanded_dockets
            
            # Docket header with expander - preserve state
            with st.expander(docket_title, expanded=is_expanded):
                # Update state when expander is opened
                if is_expanded:
                    st.session_state.expanded_dockets.add(docket_expander_key)
                else:
                    st.session_state.expanded_dockets.discard(docket_expander_key)
                # Docket metadata in horizontal layout - combine all items into single markdown
                meta_items = []
                
                # Court
                meta_items.append(f'<div class="docket-meta-item"><span class="docket-meta-label">🏛️ Court</span><span class="docket-meta-value">{html.escape(str(court))}</span></div>')
                
                # Date Filed
                meta_items.append(f'<div class="docket-meta-item"><span class="docket-meta-label">📅 Date Filed</span><span class="docket-meta-value">{html.escape(str(date_filed))}</span></div>')
                
                # Docket ID
                meta_items.append(f'<div class="docket-meta-item"><span class="docket-meta-label">🆔 Docket ID</span><span class="docket-meta-value">{html.escape(str(docket_info["docket_id"]))}</span></div>')
                
                # Documents Count
                meta_items.append(f'<div class="docket-meta-item"><span class="docket-meta-label">📄 Documents</span><span class="docket-meta-value">{num_docs}</span></div>')
                
                # Assigned To (if available)
                if docket_info.get('assigned_to'):
                    meta_items.append(f'<div class="docket-meta-item"><span class="docket-meta-label">👤 Assigned To</span><span class="docket-meta-value">{html.escape(str(docket_info["assigned_to"]))}</span></div>')
                
                # Cause (if available)
                if docket_info.get('cause'):
                    meta_items.append(f'<div class="docket-meta-item"><span class="docket-meta-label">⚖️ Cause</span><span class="docket-meta-value">{html.escape(str(docket_info["cause"]))}</span></div>')
                
                # Render all items in a single markdown call for horizontal layout
                st.markdown(f'<div class="docket-meta-grid">{"".join(meta_items)}</div>', unsafe_allow_html=True)
                
                # Full case name tooltip if truncated
                if len(case_name) > 80:
                    st.caption(f"Full case name: {case_name}")
                
                st.markdown("---")
                
                # Documents in this docket - VS Code-style tabs
                st.markdown(f"<h3 style='font-family: -apple-system, BlinkMacSystemFont, \"Segoe UI\", \"Roboto\", \"Helvetica\", \"Arial\", sans-serif; color: #1f77b4; margin-top: 20px; margin-bottom: 15px; font-weight: 600;'>📄 Documents({num_docs})</h3>", unsafe_allow_html=True)
                
                # Prepare document titles for tabs
                doc_titles = []
                for doc_idx, document in enumerate(docket_info['documents']):
                    doc_meta = document.get('source_meta', {})
                    if isinstance(doc_meta, str):
                        try:
                            doc_meta = json.loads(doc_meta)
                        except:
                            doc_meta = {}
                    
                    doc_title_raw = document.get('title') or doc_meta.get('title') or f"Document {doc_idx + 1}"
                    # Clean title - remove related document references and author info
                    doc_title = self.clean_document_title(doc_title_raw)
                    doc_type = doc_meta.get('document_type') or ''
                    
                    # Create tab title (add number prefix, truncate if too long)
                    doc_num = doc_idx + 1
                    if doc_type:
                        # Format: "1. Title • Type"
                        tab_title = f"{doc_num}. {doc_title[:35]}{'...' if len(doc_title) > 35 else ''} • {doc_type[:15]}"
                    else:
                        # Format: "1. Title"
                        tab_title = f"{doc_num}. {doc_title[:50]}{'...' if len(doc_title) > 50 else ''}"
                    
                    doc_titles.append(tab_title)
                
                # Create tabs using Streamlit's native tabs
                # Note: Streamlit tabs don't support HTML in titles, so we'll use a different approach
                if doc_titles:
                    # Create simple numbered titles for tabs (Streamlit doesn't support HTML in tab titles)
                    simple_titles = []
                    for doc_idx, document in enumerate(docket_info['documents']):
                        doc_meta = document.get('source_meta', {})
                        if isinstance(doc_meta, str):
                            try:
                                doc_meta = json.loads(doc_meta)
                            except:
                                doc_meta = {}
                        
                        doc_title_raw = document.get('title') or doc_meta.get('title') or f"Document {doc_idx + 1}"
                        doc_title = self.clean_document_title(doc_title_raw)
                        doc_type_raw = doc_meta.get('document_type') or ''
                        # Also clean doc_type in case it contains "PACER Document"
                        doc_type = self.clean_document_title(doc_type_raw) if doc_type_raw else ''
                        doc_num = doc_idx + 1
                        
                        # Make numbers prominent with bold and spacing
                        if doc_type:
                            simple_titles.append(f"【{doc_num}】 {doc_title[:30]}{'...' if len(doc_title) > 30 else ''} • {doc_type[:15]}")
                        else:
                            simple_titles.append(f"【{doc_num}】 {doc_title[:43]}{'...' if len(doc_title) > 43 else ''}")
                    
                    tabs = st.tabs(simple_titles)
                    
                    # Display content for each tab
                    for tab_idx, (tab, document) in enumerate(zip(tabs, docket_info['documents'])):
                        with tab:
                            doc_meta = document.get('source_meta', {})
                            if isinstance(doc_meta, str):
                                try:
                                    doc_meta = json.loads(doc_meta)
                                except:
                                    doc_meta = {}
                            
                            doc_title_raw = document.get('title') or doc_meta.get('title') or f"Document {tab_idx + 1}"
                            # Clean title - remove related document references and author info
                            doc_title = self.clean_document_title(doc_title_raw)
                            doc_type = doc_meta.get('document_type') or 'Document'
                            doc_id = doc_meta.get('document_id') or doc_meta.get('documentId') or ''
                            pdf_url = doc_meta.get('pdf_url') or ''
                            
                            # Document metadata with improved styling
                            st.markdown('<div class="document-metadata">', unsafe_allow_html=True)
                            doc_col1, doc_col2 = st.columns(2)
                            with doc_col1:
                                st.markdown(f"**📄 Title:** {doc_title}")
                                if doc_id:
                                    st.markdown(f"**🆔 Document ID:** {doc_id}")
                                # Replace PDF URL with View Source and Copy buttons
                                if pdf_url:
                                    import streamlit.components.v1 as components
                                    # Escape the URL for use in JavaScript (handle quotes and backslashes)
                                    escaped_url = pdf_url.replace("\\", "\\\\").replace("'", "\\'").replace('"', '\\"').replace('\n', '\\n').replace('\r', '\\r')
                                    components.html(f"""
                                    <div style="margin-top: 10px; display: flex; gap: 5px; align-items: center;">
                                        <a href="{html.escape(pdf_url)}" target="_blank" style="text-decoration: none;">
                                            <button style="background-color: #4CAF50; color: white; padding: 8px 16px; border-radius: 5px; font-weight: bold; border: none; cursor: pointer;">
                                                Source
                                            </button>
                                        </a>
                                        <button style="background-color: #4CAF50; color: white; padding: 8px 16px; border-radius: 5px; font-weight: bold; border: none; cursor: pointer;" onclick="
                                            navigator.clipboard.writeText('{escaped_url}').then(() => {{
                                                const original = this.innerText;
                                                this.innerText = '✅ Copied';
                                                setTimeout(() => this.innerText = original, 1500);
                                            }})
                                        ">📋 Copy URL</button>
                                    </div>
                                    """, height=50)
                            
                            with doc_col2:
                                tag = document.get('tag', 'Untagged')
                                st.markdown(f"**🏷️ Tag:** {self.format_tag(tag)}", unsafe_allow_html=True)
                                source = document.get('source', 'Unknown')
                                st.markdown(f"**📰 Source:** {source}")
                            
                            st.markdown('</div>', unsafe_allow_html=True)
                            st.markdown("---")
                            
                            # Summary (reason_identified) - simple display
                            reason = document.get('reason_identified', '')
                            if reason:
                                st.markdown("**Summary:**")
                                st.markdown(f'<div class="article-summary">{html.escape(str(reason))}</div>', unsafe_allow_html=True)
                                st.markdown("<br>", unsafe_allow_html=True)
                            
                            # Document content - using selectable div instead of disabled text_area
                            st.markdown("### 📝 Content")
                            content = document.get('data') or document.get('content') or 'No content available'
                            # Escape HTML special characters for safe display
                            escaped_content = html.escape(str(content))
                            st.markdown(f'<div class="selectable-content">{escaped_content}</div>', unsafe_allow_html=True)
                            
                            # Copy content button
                            if content and content != 'No content available':
                                import streamlit.components.v1 as components
                                # Escape content for JavaScript using JSON encoding (safer for all special characters)
                                escaped_content_js = json.dumps(str(content))
                                # Use a unique ID for the button to avoid conflicts
                                button_id = f"copy_content_{docket_key}_{tab_idx}"
                                components.html(f"""
                                <div style="margin-top: 10px; display: flex; gap: 5px; align-items: center;">
                                    <button id="{button_id}" style="background-color: #1f77b4; color: white; padding: 8px 16px; border-radius: 5px; font-weight: bold; border: none; cursor: pointer;">📋 Copy Content</button>
                                    <script>
                                        (function() {{
                                            const button = document.getElementById('{button_id}');
                                            const content = {escaped_content_js};
                                            button.onclick = function() {{
                                                navigator.clipboard.writeText(content).then(() => {{
                                                    const original = this.innerText;
                                                    this.innerText = '✅ Copied';
                                                    setTimeout(() => this.innerText = original, 1500);
                                                }});
                                            }};
                                        }})();
                                    </script>
                                </div>
                                """, height=50)
                            
                            st.markdown("<br>", unsafe_allow_html=True)

                            # st.markdown("<br>", unsafe_allow_html=True)
                            concerns = document.get('concerns', '')
                            risks = document.get('emerging_risk_name', '')
                            
                            st.markdown("### 📊 Classification Details")
                            col1, col2 = st.columns(2)
                            with col1:
                                if concerns and concerns[0]:
                                    concerns_list = concerns.split(';') if isinstance(concerns, str) else concerns
                                    concerns_list = [c.strip() for c in concerns_list if c.strip()]
                                    # concerns_list = [c.strip() for c in concerns if c.strip()]
                                    if concerns_list:
                                        concerns_html = "".join([f'<span class="concern-badge">🚨 {html.escape(c)}</span>' for c in concerns_list[:10]])
                                        st.markdown(f"**Concerns:**<br>{concerns_html}", unsafe_allow_html=True)
                                if document.get('misc_topics'):
                                    topics = document.get('misc_topics', '').split(';')
                                    # st.markdown("**Misc Topics:**")
                                    misc_topics = [c.strip() for c in topics if c.strip()]
                                    if misc_topics:
                                        misc_topics_html = "".join([f'<span class="misc-badge"> {html.escape(c)}</span>' for c in misc_topics[:10]])
                                        st.markdown(f"**Misc Topics:**<br>{misc_topics_html}", unsafe_allow_html=True)
                                    # for topic in topics:
                                    #     if topic.strip():
                                    #         st.write(f"• {topic.strip()}")
                            with col2:
                                if risks and risks[0]:
                                    risks_list = risks.split(';') if isinstance(risks, str) else risks
                                    risks = [c.strip() for c in risks_list if c.strip()]
                                    if risks:
                                        risks_html = "".join([f'<span class="risks-badge"> {html.escape(c)}</span>' for c in risks[:10]])
                                        st.markdown(f"**Emerging Risks:**<br>{risks_html}", unsafe_allow_html=True)
                                    # st.markdown("**Emerging Risks:**")
                                    # for risk in risks:
                                    #     if risk.strip():
                                    #         st.write(f"• {risk.strip()}")
                                naics_code = document.get('naicscode')
                                naics_desc = document.get('naics_description', '')

                                if naics_code:
                                    naics_html = f"""
                                    <div class="naics-section">
                                        <span class="naics-badge">🏢 {html.escape(str(naics_code))}</span>
                                        <span class="naics-desc">{html.escape(naics_desc)}</span>
                                    </div>
                                    """
                                    st.markdown(f"**NAICS:**<br>{naics_html}", unsafe_allow_html=True)
                                # if article.get('naicscode'):
                                #     st.markdown("**NAICS:**")
                                #     st.write(f"• Code: {article.get('naicscode')}")
                                #     st.write(f"• {article.get('naics_description', 'N/A')}")
                            st.markdown('</div>', unsafe_allow_html=True)

                            
                            # Concerns and risks - horizontal badges
                            # concerns = document.get('concerns', '')
                            # risks = document.get('emerging_risk_name', '')
                            
                            # if concerns:
                            #     concerns_list = concerns.split(';') if isinstance(concerns, str) else concerns
                            #     concerns_cleaned = [c.strip() for c in concerns_list if c.strip()]
                            #     if concerns_cleaned:
                            #         concerns_html = "".join([f'<span class="concern-badge">🚨 {html.escape(c)}</span>' for c in concerns_cleaned[:10]])
                            #         st.markdown(f"**Concerns:**<br>{concerns_html}", unsafe_allow_html=True)
                            
                            # if risks:
                            #     risks_list = risks.split(';') if isinstance(risks, str) else risks
                            #     st.markdown("**Emerging Risks:**")
                            #     for risk in risks_list[:5]:
                            #         if risk.strip():
                            #             st.markdown(f'- ⚠️ {risk.strip()}')
                            
    def render_article_card(self, article: dict, index: int):
        """Render individual article card with collapsible/expandable functionality."""
        article_id = f"article_{index}"
        is_expanded = article_id in st.session_state.expanded_articles

        # Extract article data
        title = str(article.get('title') or 'Untitled Article')[:200]
        summary = article.get('reason_identified', article.get('description', 'No summary available'))[:300]
        print(summary)
        source = article.get('source', 'Unknown Source')

        tag = article.get('tag', 'Untagged')
        url = article.get('url', '#')
        concerns = article.get('concerns', '').split(';') if article.get('concerns') else []
        risks = article.get('emerging_risk_name', '').split(';') if article.get('emerging_risk_name') else []
        date_time = article.get('published_time', 'Unknown Date')
        score = round(article.get('_score', 0), 2)

        # Build badges HTML
        badges_html = ""
        # if concerns and concerns[0]:
        #     badges_html += "<div style='margin-top: 10px;'>"
        #     for concern in concerns[:5]:
        #         if concern.strip():
        #             badges_html += f'<span class="concern-badge">🚨 {concern.strip()}</span>'
        #     badges_html += "</div>"

        # if risks and risks[0]:
        #     badges_html += "<div style='margin-top: 5px;'>"
        #     for risk in risks[:5]:
        #         if risk.strip():
        #             badges_html += f'<span class="risk-badge">⚠️ {risk.strip()}</span>'
        #     badges_html += "</div>"

        # Track expander state to preserve after rerun
        article_expander_key = f"article_exp_{article_id}"
        is_article_expanded = article_expander_key in st.session_state.expanded_articles
        
        # Use st.expander for the whole card - preserve state
        with st.expander(f"{title} ({date_time[:10] if date_time != 'Unknown Date' else date_time})  ({tag}) ({score})", expanded=is_article_expanded):
            # Update state when expander is opened
            if is_article_expanded:
                st.session_state.expanded_articles.add(article_expander_key)
            else:
                st.session_state.expanded_articles.discard(article_expander_key)
            # Summary - simple display
            st.markdown("**Summary:**")
            st.markdown(f'<div class="article-summary">{html.escape(str(summary))}</div>', unsafe_allow_html=True)
            
            st.markdown("<br>", unsafe_allow_html=True)
            
            # Article meta
            st.markdown(f"""
            <div class="article-meta">
                <span class="meta-item">📰 {source}</span>
                <span>{self.format_tag(tag)}</span>
            </div>
            {badges_html}
            """, unsafe_allow_html=True)

            # Buttons for source & copy link
            col1, col2 = st.columns([1,1])
            with col2:
                if url and url != '#':
                    import streamlit.components.v1 as components
                    components.html(f"""
                    <div style="display: flex; gap: 5px; align-items: center;">
                        <a href="{url}" target="_blank" style="text-decoration: none;">
                            <button style="background-color: #4CAF50; color: white; padding: 5px 12px; border-radius: 5px; font-weight: bold; display: inline-block;">Source</button>
                        </a>
                        <button style="background-color: #4CAF50; color: white; padding: 5px 12px; border-radius: 5px; font-weight: bold; display: inline-block;" onclick="
                            navigator.clipboard.writeText('{url}').then(() => {{
                                const original = this.innerText;
                                this.innerText = '✅ Copied';
                                setTimeout(() => this.innerText = original, 1500);
                            }})
                        ">📋 Copy</button>
                    </div>
                    """, height=50)

            # Full details inside the expander
            st.markdown('<div class="full-content">', unsafe_allow_html=True)
            st.markdown("### 📄 Full Article Content")
            full_data = article.get('data', 'No full content available')
            # Use selectable div for consistency with CourtListener
            escaped_content = html.escape(str(full_data))
            st.markdown(f'<div class="selectable-content">{escaped_content}</div>', unsafe_allow_html=True)

            # Additional metadata
            st.markdown("### 📊 Classification Details")
            col1, col2 = st.columns(2)
            with col1:
                if concerns and concerns[0]:
                    concerns_list = [c.strip() for c in concerns if c.strip()]
                    if concerns_list:
                        concerns_html = "".join([f'<span class="concern-badge">🚨 {html.escape(c)}</span>' for c in concerns_list[:10]])
                        st.markdown(f"**Concerns:**<br>{concerns_html}", unsafe_allow_html=True)
                if article.get('misc_topics'):
                    topics = article.get('misc_topics', '').split(';')
                    # st.markdown("**Misc Topics:**")
                    misc_topics = [c.strip() for c in topics if c.strip()]
                    if misc_topics:
                        misc_topics_html = "".join([f'<span class="misc-badge"> {html.escape(c)}</span>' for c in misc_topics[:10]])
                        st.markdown(f"**Misc Topics:**<br>{misc_topics_html}", unsafe_allow_html=True)
                    # for topic in topics:
                    #     if topic.strip():
                    #         st.write(f"• {topic.strip()}")
            with col2:
                if risks and risks[0]:
                    risks = [c.strip() for c in risks if c.strip()]
                    if risks:
                        risks_html = "".join([f'<span class="risks-badge"> {html.escape(c)}</span>' for c in risks[:10]])
                        st.markdown(f"**Emerging Risks:**<br>{risks_html}", unsafe_allow_html=True)
                    # st.markdown("**Emerging Risks:**")
                    # for risk in risks:
                    #     if risk.strip():
                    #         st.write(f"• {risk.strip()}")
                naics_code = article.get('naicscode')
                naics_desc = article.get('naics_description', '')

                if naics_code:
                    naics_html = f"""
                    <div class="naics-section">
                        <span class="naics-badge">🏢 {html.escape(str(naics_code))}</span>
                        <span class="naics-desc">{html.escape(naics_desc)}</span>
                    </div>
                    """
                    st.markdown(f"**NAICS:**<br>{naics_html}", unsafe_allow_html=True)
                # if article.get('naicscode'):
                #     st.markdown("**NAICS:**")
                #     st.write(f"• Code: {article.get('naicscode')}")
                #     st.write(f"• {article.get('naics_description', 'N/A')}")
            st.markdown('</div>', unsafe_allow_html=True)

    def display_results(self, results):
        """Display query results in card format."""
        if results is None:
            st.warning("No results returned from the query.")
            return
        
        if not results:
            st.warning("No results found for your query.")
            return

        # Check if results is a string (malformed response)
        if isinstance(results, str):
            if results == "ERROR" or "ERROR" in results:
                st.error("❌ Query execution failed on the backend. The API returned an error.")
                return
            else:
                st.error("❌ Unexpected string response from API")
                with st.expander("View raw response"):
                    st.text(results)
                return

        # Check if results contain an error dictionary
        if isinstance(results, dict) and "ERROR" in results:
            st.error(f"❌ Query Error: {results['ERROR'].get('message', 'Unknown error')}")
            return

        # 🔍 Normalize OpenSearch result format
        if isinstance(results, dict):
            if "hits" in results:
                hits = results.get("hits", {}).get("hits", [])
                # results = [hit.get("_source", {}) for hit in hits]
                results = []
                for hit in hits:
                    article = hit.get("_source", {})
                    article["_score"] = hit.get("_score", 0)
                    results.append(article)
            elif "results" in results:
                # Handle nested results structure
                results = results.get("results", [])
            else:
                # Try to treat the dict as a single result
                results = [results]

        if not isinstance(results, list):
            st.error("❌ Unexpected results format — expected a list of articles.")
            with st.expander("View raw response (for debugging)"):
                st.json(results)
            return

        if len(results) == 0:
            st.warning("⚠️ No matching records found.")
            return

        # Check if we should group by docket (CourtListener only)
        source_filter = st.session_state.get('source_filter_toggle', 'Others')
        if source_filter == "CourtListener":
            # Group CourtListener documents by docket
            dockets = self.group_courtlistener_by_docket(results)
            
            # Convert dockets to a list of all documents for filtering
            all_courtlistener_docs = []
            for docket_info in dockets.values():
                all_courtlistener_docs.extend(docket_info['documents'])
            
            # Create DataFrame for filtering (similar to Others view)
            if all_courtlistener_docs:
                df = pd.DataFrame(all_courtlistener_docs)
            else:
                df = pd.DataFrame()
            
            # Calculate and display INITIAL statistics (before filtering)
            initial_stats_dockets = dockets
            total_documents_initial = sum(len(d['documents']) for d in initial_stats_dockets.values())
            current_count_initial = sum(1 for d in initial_stats_dockets.values() 
                                       for doc in d['documents'] 
                                       if doc.get('tag') == 'Current')
            trend_count_initial = sum(1 for d in initial_stats_dockets.values() 
                                     for doc in d['documents'] 
                                     if doc.get('tag') == 'Potential New Trend')
            untagged_count_initial = sum(1 for d in initial_stats_dockets.values() 
                                       for doc in d['documents'] 
                                       if doc.get('tag', '') in ['Untagged', '', None] or not doc.get('tag'))
            
            # Display statistics boxes FIRST
            st.markdown('<div style="margin-bottom: 0; padding-bottom: 0;">', unsafe_allow_html=True)
            col1, col2, col3, col4 = st.columns(4)
            with col1:
                st.markdown(f"""
                <div class="stats-box">
                    <h2 style="color:#1f77b4;">Total Records</h2>
                    <h3>{total_documents_initial}</h3>
                </div>
                """, unsafe_allow_html=True)
            with col2:
                st.markdown(f"""
                <div class="stats-box">
                    <h2 style="color:#4CAF50;">Current</h2>
                    <h3>{current_count_initial}</h3>
                </div>
                """, unsafe_allow_html=True)
            with col3:
                st.markdown(f"""
                <div class="stats-box">
                    <h2 style="color:#FF9800;">New Trends</h2>
                    <h3>{trend_count_initial}</h3>
                </div>
                """, unsafe_allow_html=True)
            with col4:
                st.markdown(f"""
                <div class="stats-box">
                    <h2 style="color:#9E9E9E;">Untagged</h2>
                    <h3>{untagged_count_initial}</h3>
                </div>
                """, unsafe_allow_html=True)
            st.markdown('</div>', unsafe_allow_html=True)
            # Filters for CourtListener - NOW SHOWN AFTER STATISTICS
            # Initialize filtered_dockets variable for download functionality
            filtered_dockets = None
            
            if not df.empty:
                st.markdown('<div class="filter-section" style="margin-top: 0; padding-top: 0;">', unsafe_allow_html=True)
                st.markdown("### Filter Results")
                
                filter_col1, filter_col2, filter_col3, filter_col4 = st.columns(4)
                
                # Store original df for reference
                original_df = df.copy()
                
                with filter_col1:
                    if 'tag' in df.columns:
                        # Get unique tags, handling NaN values
                        unique_tags = [t for t in df['tag'].dropna().unique().tolist() if t]
                        if unique_tags:
                            tag_filter = st.multiselect(
                                "Filter by Tag:",
                                options=unique_tags,
                                key="courtlistener_tag_filter"
                            )
                            if tag_filter:
                                df = df[df['tag'].isin(tag_filter)]
                
                with filter_col2:
                    if 'source' in df.columns:
                        # Get unique sources, handling NaN values
                        unique_sources = [s for s in df['source'].dropna().unique().tolist() if s]
                        if unique_sources:
                            source_filter = st.multiselect(
                                "Filter by source:",
                                options=unique_sources,
                                key="courtlistener_source_filter"
                            )
                            if source_filter:
                                df = df[df['source'].isin(source_filter)]
                
                with filter_col3:
                    sort_by = st.selectbox(
                        "Sort by:",
                        options=["Most Relevant" ,"Most Recent", "Title A-Z", "Source"],
                        key="courtlistener_sort_option"
                    )
                
                with filter_col4:
                    items_per_page = st.selectbox(
                        "Items per page:",
                        options=[1, 5, 10, 20],
                        index=2,
                        key="courtlistener_items_per_page"
                    )
            else:
                # No documents - set default items_per_page (use default 10 if not in session state)
                items_per_page = st.session_state.get('courtlistener_items_per_page', 10) if 'courtlistener_items_per_page' in st.session_state else 10
            
            # Apply sorting and filtering if df is not empty
            if not df.empty:
                st.markdown('</div>', unsafe_allow_html=True)
                
                # Apply sorting to DataFrame
                sort_by = st.session_state.get('courtlistener_sort_option', 'Most Recent')
                if sort_by == "Most Relevant":
                    if '_score' in df.columns:
                        df = df.sort_values('_score', ascending=False, na_position='last')
                elif sort_by == "Most Recent":
                    if 'published_time' in df.columns:
                        df = df.sort_values('published_time', ascending=False, na_position='last')
                    elif 'date_time' in df.columns:
                        df = df.sort_values('date_time', ascending=False, na_position='last')
                elif sort_by == "Title A-Z":
                    if 'title' in df.columns:
                        df = df.sort_values('title', ascending=True, na_position='last')
                elif sort_by == "Source":
                    if 'source' in df.columns:
                        df = df.sort_values('source', ascending=True, na_position='last')
                
                # Rebuild dockets dict with filtered documents
                if not df.empty:
                    # Get filtered documents as a list of dicts
                    filtered_docs_list = df.to_dict('records')
                    
                    # Create lookup sets - normalize all values to strings for consistent matching
                    filtered_urls = set()
                    filtered_doc_ids = set()
                    for doc in filtered_docs_list:
                        url = doc.get('url')
                        doc_id = doc.get('doc_id')
                        if url is not None:
                            filtered_urls.add(str(url).strip().lower())
                        if doc_id is not None:
                            # Handle both int and string doc_ids
                            filtered_doc_ids.add(str(doc_id).strip())
                    
                    # Store original documents for reference
                    original_dockets = dockets.copy()
                    
                    # Filter dockets to only include documents that are in the filtered set
                    filtered_dockets = {}
                    for docket_id, docket_info in original_dockets.items():
                        filtered_docs = []
                        for doc in docket_info['documents']:
                            doc_url = str(doc.get('url', '')).strip().lower() if doc.get('url') else ''
                            doc_id = str(doc.get('doc_id', '')).strip() if doc.get('doc_id') is not None else ''
                            
                            # Match by URL (case-insensitive) or doc_id
                            url_match = doc_url and doc_url in filtered_urls
                            id_match = doc_id and doc_id in filtered_doc_ids
                            
                            if url_match or id_match:
                                filtered_docs.append(doc)
                        
                        # Only include docket if it has filtered documents
                        if filtered_docs:
                            filtered_dockets[docket_id] = {**docket_info, 'documents': filtered_docs}
                    
                    # Apply sorting to dockets based on sort_by option
                    if sort_by == "Title A-Z":
                        # Sort dockets by case name
                        filtered_dockets = dict(sorted(filtered_dockets.items(), 
                                                      key=lambda x: x[1].get('case_name', '').lower()))
                    elif sort_by == "Most Recent":
                        # Sort dockets by date_filed (most recent first)
                        filtered_dockets = dict(sorted(filtered_dockets.items(), 
                                                      key=lambda x: x[1].get('date_filed', ''), 
                                                      reverse=True))
                    elif sort_by == "Most Relevant":
                        # Sort dockets by case name
                        filtered_dockets = dict(sorted(filtered_dockets.items(), 
                                                      key=lambda x: x[1].get('_score', '').lower()))
                    elif sort_by == "Source":
                        # Sort dockets by source (all CourtListener, so this may not be useful)
                        filtered_dockets = dict(sorted(filtered_dockets.items(), 
                                                      key=lambda x: x[1].get('case_name', '').lower()))
                    
                    # Store filtered dockets for statistics (BEFORE pagination)
                    all_filtered_dockets = filtered_dockets.copy()
                    
                    # Calculate pagination
                    docket_items = list(filtered_dockets.items())
                    total_dockets = len(docket_items)
                    total_pages = (total_dockets + items_per_page - 1) // items_per_page if total_dockets > 0 else 1
                    
                    # Initialize current page for CourtListener
                    if 'courtlistener_current_page' not in st.session_state:
                        st.session_state.courtlistener_current_page = 1
                    
                    # Apply pagination - limit number of dockets shown based on current page
                    start_idx = (st.session_state.courtlistener_current_page - 1) * items_per_page
                    end_idx = min(start_idx + items_per_page, total_dockets)
                    dockets = dict(docket_items[start_idx:end_idx])
                else:
                    # No documents match filters - show empty
                    dockets = {}
                    all_filtered_dockets = {}
                    total_dockets = 0
                    total_pages = 1
                    if 'courtlistener_current_page' not in st.session_state:
                        st.session_state.courtlistener_current_page = 1
            else:
                # No filters section shown (df.empty) - use all dockets with pagination
                # Get items_per_page from session state or use default (10)
                items_per_page = st.session_state.get('courtlistener_items_per_page', 10) if 'courtlistener_items_per_page' in st.session_state else 10
                
                docket_items = list(dockets.items())
                total_dockets = len(docket_items)
                total_pages = (total_dockets + items_per_page - 1) // items_per_page if total_dockets > 0 else 1
                
                # Initialize current page for CourtListener
                if 'courtlistener_current_page' not in st.session_state:
                    st.session_state.courtlistener_current_page = 1
                
                # Apply pagination
                start_idx = (st.session_state.courtlistener_current_page - 1) * items_per_page
                end_idx = min(start_idx + items_per_page, total_dockets)
                dockets = dict(docket_items[start_idx:end_idx])
            
            st.markdown("---")
            st.markdown('<h2 style="color: #1f77b4; margin-bottom: 20px; font-size: 1.5rem;">⚖️ CourtListener Dockets</h2>', unsafe_allow_html=True)
            
            # Display page info
            if total_dockets > 0:
                dockets_shown = len(dockets)
                st.markdown(f"### 📋 Showing {dockets_shown} of {total_dockets} dockets")
            
            # Display dockets with better spacing
            docket_list = list(dockets.items())
            for idx, (docket_key, docket_info) in enumerate(docket_list):
                self.render_courtlistener_docket(docket_info, docket_key)
                # Add spacing between dockets (except for last one)
                if idx < len(docket_list) - 1:
                    st.markdown("<br>", unsafe_allow_html=True)
            
            # Pagination controls for CourtListener
            if total_pages > 1:
                st.markdown("---")
                col1, col2, col3, col4, col5 = st.columns([1, 1, 2, 1, 1])
                
                with col1:
                    if st.button("⏮️ First", disabled=st.session_state.courtlistener_current_page == 1, key="courtlistener_first"):
                        st.session_state.courtlistener_current_page = 1
                        st.rerun()
                
                with col2:
                    if st.button("◀️ Previous", disabled=st.session_state.courtlistener_current_page == 1, key="courtlistener_prev"):
                        st.session_state.courtlistener_current_page -= 1
                        st.rerun()
                
                with col3:
                    st.markdown(f"<p style='text-align: center'>Page {st.session_state.courtlistener_current_page} of {total_pages}</p>", unsafe_allow_html=True)
                
                with col4:
                    if st.button("Next ▶️", disabled=st.session_state.courtlistener_current_page == total_pages, key="courtlistener_next"):
                        st.session_state.courtlistener_current_page += 1
                        st.rerun()
                
                with col5:
                    if st.button("Last ⏭️", disabled=st.session_state.courtlistener_current_page == total_pages, key="courtlistener_last"):
                        st.session_state.courtlistener_current_page = total_pages
                        st.rerun()
            
            # Download options for CourtListener
            # Prepare download data - use filtered documents if filters were applied, otherwise use all documents
            download_docs = []
            if filtered_dockets is not None and filtered_dockets:
                # Filters were applied - use filtered documents from all filtered dockets (not just paginated ones)
                for docket_info in filtered_dockets.values():
                    download_docs.extend(docket_info['documents'])
            elif all_courtlistener_docs:
                # No filters applied - use all documents
                download_docs = all_courtlistener_docs
            
            if download_docs:
                st.markdown("---")
                st.markdown("### 💾 Export Data")
                
                # Prepare data for download - flatten all documents
                download_df = pd.DataFrame(download_docs)
                
                # Remove unwanted fields: chunk_id, chunk_text, chunk_vector
                fields_to_remove = ['chunk_id', 'chunk_text', 'chunk_vector']
                for field in fields_to_remove:
                    if field in download_df.columns:
                        download_df = download_df.drop(columns=[field])
                
                col1, col2 = st.columns(2)
                
                with col1:
                    csv = download_df.to_csv(index=False)
                    st.download_button(
                        label="📥 Download as CSV",
                        data=csv,
                        file_name=f"courtlistener_results_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                        mime="text/csv"
                    )
                
                with col2:
                    json_str = download_df.to_json(orient='records', indent=2)
                    st.download_button(
                        label="📥 Download as JSON",
                        data=json_str,
                        file_name=f"courtlistener_results_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json",
                        mime="application/json"
                    )
            
            return

        # ✅ Now safe to process results (for RSS and other sources)
        df = pd.DataFrame(results)
        
        # Display statistics
        st.markdown('<div style="margin-bottom: 0; padding-bottom: 0;">', unsafe_allow_html=True)
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.markdown(f"""
            <div class="stats-box">
                <h2 style="color:#1f77b4;">Total Records</h2>
                <h3>{len(df)}</h3>
            </div>
            """, unsafe_allow_html=True)
        
        with col2:
            current_count = len(df[df.get('tag', '') == 'Current']) if 'tag' in df.columns else 0
            st.markdown(f"""
            <div class="stats-box">
                <h2 style="color:#4CAF50;">Current</h2>
                <h3>{current_count}</h3>
            </div>
            """, unsafe_allow_html=True)
        
        with col3:
            trend_count = len(df[df.get('tag', '') == 'Potential New Trend']) if 'tag' in df.columns else 0
            st.markdown(f"""
            <div class="stats-box">
                <h2 style="color:#FF9800;">New Trends</h2>
                <h3>{trend_count}</h3>
            </div>
            """, unsafe_allow_html=True)
        
        with col4:
            untagged_count = len(df[df.get('tag', '').isin(['Untagged', '', None])]) if 'tag' in df.columns else 0
            st.markdown(f"""
            <div class="stats-box">
                <h2 style="color:#9E9E9E;">Untagged</h2>
                <h3>{untagged_count}</h3>
            </div>
            """, unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)
        # Filters
        st.markdown('<div class="filter-section" style="margin-top: 0; padding-top: 0;">', unsafe_allow_html=True)
        st.markdown("### Filter Results")
        
        filter_col1, filter_col2, filter_col3, filter_col4 = st.columns(4)
        
        with filter_col1:
            if 'tag' in df.columns:
                tag_filter = st.multiselect(
                    "Filter by Tag:",
                    options=df['tag'].unique().tolist(),
                    key="tag_filter"
                )
                if tag_filter:
                    df = df[df['tag'].isin(tag_filter)]
        
        with filter_col2:
            if 'source' in df.columns:
                source_filter = st.multiselect(
                    "Filter by source:",
                    options=df['source'].dropna().unique().tolist(),
                    key="source_filter"
                )
                if source_filter:
                    df = df[df['source'].isin(source_filter)]
        
        with filter_col3:
            sort_by = st.selectbox(
                "Sort by:",
                options=["Most Relevant", "Most Recent", "Title A-Z", "Source"],
                key="sort_option"
            )
        
        with filter_col4:
            items_per_page = st.selectbox(
                "Items per page:",
                options=[10, 20, 50, 100],
                index=1,
                key="items_per_page"
            )
        
        st.markdown('</div>', unsafe_allow_html=True)
        
        # Apply sorting
        if sort_by == "Most Recent" and 'date_time' in df.columns:
            df = df.sort_values('date_time', ascending=False)
        elif sort_by == "Title A-Z" and 'title' in df.columns:
            df = df.sort_values('title')
        elif sort_by == "source" and 'source' in df.columns:
            df = df.sort_values('source')
        
        # Pagination
        total_items = len(df)
        total_pages = (total_items + items_per_page - 1) // items_per_page
        
        if 'current_page' not in st.session_state:
            st.session_state.current_page = 1
        
        # Display articles
        st.markdown(f"### 📋 Showing {min(items_per_page, total_items)} of {total_items} articles")
        
        start_idx = (st.session_state.current_page - 1) * items_per_page
        end_idx = min(start_idx + items_per_page, total_items)
        
        # Render article cards
        for idx in range(start_idx, end_idx):
            self.render_article_card(df.iloc[idx].to_dict(), idx)
            
        # Pagination controls
        if total_pages > 1:
            st.markdown("---")
            col1, col2, col3, col4, col5 = st.columns([1, 1, 2, 1, 1])
            
            with col1:
                if st.button("⏮️ First", disabled=st.session_state.current_page == 1):
                    st.session_state.current_page = 1
                    st.rerun()
            
            with col2:
                if st.button("◀️ Previous", disabled=st.session_state.current_page == 1):
                    st.session_state.current_page -= 1
                    st.rerun()
            
            with col3:
                st.markdown(f"<p style='text-align: center'>Page {st.session_state.current_page} of {total_pages}</p>", unsafe_allow_html=True)
            
            with col4:
                if st.button("Next ▶️", disabled=st.session_state.current_page == total_pages):
                    st.session_state.current_page += 1
                    st.rerun()
            
            with col5:
                if st.button("Last ⏭️", disabled=st.session_state.current_page == total_pages):
                    st.session_state.current_page = total_pages
                    st.rerun()
        
        # Download options
        st.markdown("---")
        st.markdown("### 💾 Export Data")
        
        # Remove unwanted fields: chunk_id, chunk_text, chunk_vector
        download_df = df.copy()
        fields_to_remove = ['chunk_id', 'chunk_text', 'chunk_vector']
        for field in fields_to_remove:
            if field in download_df.columns:
                download_df = download_df.drop(columns=[field])
        
        col1, col2 = st.columns(2)
        
        with col1:
            csv = download_df.to_csv(index=False)
            st.download_button(
                label="📥 Download as CSV",
                data=csv,
                file_name=f"insurance_query_results_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                mime="text/csv"
            )
        
        with col2:
            json_str = download_df.to_json(orient='records', indent=2)
            st.download_button(
                label="📥 Download as JSON",
                data=json_str,
                file_name=f"insurance_query_results_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json",
                mime="application/json"
            )
    
    def render_sidebar(self):
        """Render sidebar with query examples and reference data."""
        st.sidebar.title("Query Assistant")
        
        st.sidebar.markdown("### 📊 Example Queries")
        
        st.sidebar.markdown("---")
        st.sidebar.markdown("**FAQs:**")
        
        examples = [
            "Show all articles tagged as Current",
            "Find articles about Climate Change",
            "Show articles with lawsuits or property damage concerns",
            "Find Potential New Trend articles about PFAS",
            "Show articles from Construction Industry",
            "Find articles about ransomware and cyber attacks",
            "Show untagged articles",
            "Find articles about electric vehicles",
            "Show articles with NAICS code 524126"
        ]
        
        for i, example in enumerate(examples):
            if st.sidebar.button(example, key=f"example_{i}"):
                st.session_state.query_text = example
                st.session_state.last_query = example
                st.session_state.current_page = 1
                st.rerun()
        
        st.sidebar.markdown("---")
        st.sidebar.markdown("### 📚 Reference Data")
        
        with st.sidebar.expander("🚨 Concerns Available"):
            st.write(", ".join(concerns_events) + "...")
            
        with st.sidebar.expander("⚠️ Emerging Risks Available"):
            st.write(", ".join(emerging_risks) + "...")
        
        with st.sidebar.expander("📌 Misc Topics Available"):
            st.write(", ".join(misc_topics))
        
        with st.sidebar.expander("🏭 NAICS Codes"):
            st.write(f"Total codes available: {len(naics_data)}")
            st.write("Sample:", ", ".join([f"{n['code']}" for n in naics_data]) + "...")

    # def run(self):
    #     """Main application loop."""
    #     st.markdown('<h1 class="main-header"> Emerging Insights Query System</h1>', unsafe_allow_html=True)
    #     st.markdown('<p class="sub-header">Search and analyze insurance-related articles using natural language queries</p>', unsafe_allow_html=True)

    #     self.render_sidebar()

    #     # Initialize default session state variables if not already set
    #     if "query_text" not in st.session_state:
    #         st.session_state.query_text = ""          # bound to the text_area widget
    #     if "last_query" not in st.session_state:
    #         st.session_state.last_query = ""          # saved/committed query (history)
    #     if "last_source_filter" not in st.session_state:
    #         st.session_state.last_source_filter = None
    #     if "query_results" not in st.session_state:
    #         st.session_state.query_results = None
    #     if "expanded_articles" not in st.session_state:
    #         st.session_state.expanded_articles = set()
    #     if "current_page" not in st.session_state:
    #         st.session_state.current_page = 1

    #     # Text area bound to query_text (widget key)
    #     st.text_area(
    #         "Describe what you're looking for:",
    #         key="query_text",
    #         height=100,
    #         placeholder="Example: Show me all articles about climate change with property damage concerns..."
    #     )

    #     # Read the live widget value
    #     query_input = st.session_state.query_text

    #     # Source filter toggle
    #     source_filter = st.radio(
    #         "Source:",
    #         options=["Others", "CourtListener"],
    #         index=0,
    #         key="source_filter_toggle",
    #         help="Filter results by data source",
    #         horizontal=True,
    #         format_func=lambda x: "Others (RSS & Proquest)" if x == "Others" else x
    #     )

    #     # Clear cached results if source filter changed
    #     if (
    #         st.session_state.last_source_filter is not None
    #         and st.session_state.last_source_filter != source_filter
    #         and st.session_state.query_results is not None
    #     ):
    #         st.session_state.query_results = None
    #         st.session_state.expanded_articles = set()
    #         st.info("ℹ️ Source filter changed. Please search again to see results for the selected source.")

    #     col1, col2, col3 = st.columns([1, 1, 3])

    #     with col1:
    #         search_button = st.button("🔎 Search", type="primary")

    #     with col2:
    #         clear_button = st.button("🗑️ Clear")

    #     # Clear button resets everything (clear both widget and saved last_query)
    #     if clear_button:
    #         st.session_state.query_text = ""
    #         st.session_state.last_query = ""
    #         st.session_state.query_results = None
    #         st.session_state.current_page = 1
    #         st.session_state.expanded_articles = set()
    #         st.rerun()

    #     # Handle search
    #     if search_button and query_input.strip():
    #         with st.spinner("🤖 Generating and executing query..."):
    #             payload = {"query": query_input}
    #             if source_filter == "CourtListener":
    #                 payload["source"] = "court_listener"
    #             else:
    #                 payload["source"] = "other"

    #             try:
    #                 response = requests.post(
    #                     os.getenv("BASE_URL") + os.getenv("SEARCH_API"),
    #                     json=payload,
    #                     timeout=300
    #                 )

    #                 # Process API response
    #                 if response.status_code == 200:
    #                     try:
    #                         data = response.json()
    #                     except requests.exceptions.JSONDecodeError:
    #                         st.error("❌ Invalid JSON response from API")
    #                         with st.expander("View raw response"):
    #                             st.text(response.text)
    #                         return

    #                     with st.expander("🐛 Debug: Raw API Response", expanded=False):
    #                         st.json(data)

    #                     if "ERROR" in data:
    #                         st.error(f"❌ API Error: {data['ERROR'].get('message', 'Unknown error')}")
    #                         return

    #                     # Debug query details
    #                     with st.expander("🔧 OpenSearch Query Details", expanded=False):
    #                         query_params = data.get("query_params", {})
    #                         st.json(query_params)
    #                         st.markdown("---")
    #                         st.markdown("**Query Summary:**")
    #                         st.markdown(f"- **Source Filter:** `{data.get('source_filter', 'None')}`")
    #                         st.markdown(f"- **User Query:** `{data.get('user_query', 'None')}`")

    #                         results = data.get("results", {})
    #                         if isinstance(results, dict) and "hits" in results:
    #                             total = results.get("hits", {}).get("total", {})
    #                             total_count = total.get("value", 0) if isinstance(total, dict) else total
    #                             st.markdown(f"- **Total Hits:** `{total_count}`")

    #                             hits = results.get("hits", {}).get("hits", [])
    #                             if hits:
    #                                 sample_sources = {
    #                                     hit.get("_source", {}).get("source", "unknown")
    #                                     for hit in hits[:5]
    #                                 }
    #                                 st.markdown(f"- **Sample Sources Found:** `{', '.join(sorted(sample_sources))}`")

    #                     # Handle result data
    #                     results = data.get("results")
    #                     if results is None:
    #                         if "hits" in data:
    #                             results = data
    #                         elif "data" in data:
    #                             results = data.get("data")
    #                         else:
    #                             st.error("❌ No 'results' field found in API response")
    #                             return

    #                     if isinstance(results, str) and results == "ERROR":
    #                         st.error("❌ Query execution failed on the backend")
    #                         st.info("💡 Check your backend API logs for details")
    #                         return

    #                     # Store results in session state
    #                     st.session_state.query_results = results

    #                     # ✅ Save the committed query into last_query (different key than the widget)
    #                     st.session_state.last_query = query_input
    #                     st.session_state.last_source_filter = source_filter

    #                     # Track query history
    #                     if "query_history" not in st.session_state:
    #                         st.session_state.query_history = []
    #                     if query_input not in st.session_state.query_history:
    #                         st.session_state.query_history.append(query_input)

    #                 elif response.status_code == 400:
    #                     st.error("❌ Bad Request (400): Check your query syntax")
    #                     with st.expander("View error response"):
    #                         st.text(response.text)
    #                 elif response.status_code == 500:
    #                     st.error("❌ Server Error (500): The backend encountered an error")
    #                     with st.expander("View error response"):
    #                         st.text(response.text)
    #                 else:
    #                     st.error(f"❌ HTTP Error {response.status_code}")
    #                     with st.expander("View error response"):
    #                         st.text(response.text)

    #             except requests.exceptions.ConnectionError:
    #                 st.error("❌ Connection Error: Cannot connect to the API server.")
    #                 st.info(f"💡 Make sure the backend is running on {config['api']['backend_url']}")
    #             except requests.exceptions.Timeout:
    #                 st.error("❌ Timeout Error: The API request took too long.")
    #             except Exception as e:
    #                 st.error(f"⚠️ Unexpected Error: {str(e)}")
    #                 logger.error(f"Query execution error: {e}", exc_info=True)

    #     # Display results if available
    #     if st.session_state.query_results is not None:
    #         st.markdown("---")
    #         self.display_results(st.session_state.query_results)

    def run(self):
        """Main application loop."""
        st.markdown('<h1 class="main-header"> Emerging Insights Query System</h1>', unsafe_allow_html=True)
        st.markdown('<p class="sub-header">Search and analyze insurance-related articles using natural language queries</p>', unsafe_allow_html=True)

        self.render_sidebar()

        # Initialize default session state variables if not already set
        if "query_text" not in st.session_state:
            st.session_state.query_text = ""          # bound to the text_area widget
        if "last_query" not in st.session_state:
            st.session_state.last_query = ""          # saved/committed query (history)
        if "last_source_filter" not in st.session_state:
            st.session_state.last_source_filter = None
        if "query_results" not in st.session_state:
            st.session_state.query_results = None
        if "expanded_articles" not in st.session_state:
            st.session_state.expanded_articles = set()
        if "current_page" not in st.session_state:
            st.session_state.current_page = 1
        if "clear_trigger" not in st.session_state:
            st.session_state.clear_trigger = False

        # Handle clear trigger BEFORE creating the widget
        if st.session_state.clear_trigger:
            st.session_state.query_text = ""
            st.session_state.last_query = ""
            st.session_state.query_results = None
            st.session_state.current_page = 1
            st.session_state.expanded_articles = set()
            st.session_state.clear_trigger = False
            st.rerun()

        # Text area bound to query_text (widget key)
        st.text_area(
            "Describe what you're looking for:",
            key="query_text",
            height=100,
            placeholder="Example: Show me all articles about climate change with property damage concerns..."
        )

        # Read the live widget value
        query_input = st.session_state.query_text

        # Source filter toggle
        source_filter = st.radio(
            "Source:",
            options=["Others", "CourtListener"],
            index=0,
            key="source_filter_toggle",
            help="Filter results by data source",
            horizontal=True,
            format_func=lambda x: "Others (RSS & Proquest)" if x == "Others" else x
        )

        # Clear cached results if source filter changed
        if (
            st.session_state.last_source_filter is not None
            and st.session_state.last_source_filter != source_filter
            and st.session_state.query_results is not None
        ):
            st.session_state.query_results = None
            st.session_state.expanded_articles = set()
            st.info("ℹ️ Source filter changed. Please search again to see results for the selected source.")

        col1, col2, col3 = st.columns([1, 1, 3])

        with col1:
            search_button = st.button("🔎 Search", type="primary")

        with col2:
            clear_button = st.button("🗑️ Clear")

        # Clear button sets a trigger flag instead of directly modifying
        if clear_button:
            st.session_state.clear_trigger = True
            st.rerun()

        # Handle search
        if search_button and query_input.strip():
            with st.spinner("🤖 Generating and executing query..."):
                payload = {"query": query_input}
                if source_filter == "CourtListener":
                    payload["source"] = "court_listener"
                else:
                    payload["source"] = "other"

                try:
                    response = requests.post(
                        os.getenv("BASE_URL") + os.getenv("SEARCH_API"),
                        json=payload,
                        timeout=300
                    )

                    # Process API response
                    if response.status_code == 200:
                        try:
                            data = response.json()
                        except requests.exceptions.JSONDecodeError:
                            st.error("❌ Invalid JSON response from API")
                            with st.expander("View raw response"):
                                st.text(response.text)
                            return

                        with st.expander("🐛 Debug: Raw API Response", expanded=False):
                            st.json(data)

                        if "ERROR" in data:
                            st.error(f"❌ API Error: {data['ERROR'].get('message', 'Unknown error')}")
                            return

                        # Debug query details
                        with st.expander("🔧 OpenSearch Query Details", expanded=False):
                            query_params = data.get("query_params", {})
                            st.json(query_params)
                            st.markdown("---")
                            st.markdown("**Query Summary:**")
                            st.markdown(f"- **Source Filter:** `{data.get('source_filter', 'None')}`")
                            st.markdown(f"- **User Query:** `{data.get('user_query', 'None')}`")

                            results = data.get("results", {})
                            if isinstance(results, dict) and "hits" in results:
                                total = results.get("hits", {}).get("total", {})
                                total_count = total.get("value", 0) if isinstance(total, dict) else total
                                st.markdown(f"- **Total Hits:** `{total_count}`")

                                hits = results.get("hits", {}).get("hits", [])
                                if hits:
                                    sample_sources = {
                                        hit.get("_source", {}).get("source", "unknown")
                                        for hit in hits[:5]
                                    }
                                    st.markdown(f"- **Sample Sources Found:** `{', '.join(sorted(sample_sources))}`")

                        # Handle result data
                        results = data.get("results")
                        if results is None:
                            if "hits" in data:
                                results = data
                            elif "data" in data:
                                results = data.get("data")
                            else:
                                st.error("❌ No 'results' field found in API response")
                                return

                        if isinstance(results, str) and results == "ERROR":
                            st.error("❌ Query execution failed on the backend")
                            st.info("💡 Check your backend API logs for details")
                            return

                        # Store results in session state
                        st.session_state.query_results = results

                        # ✅ Save the committed query into last_query (different key than the widget)
                        st.session_state.last_query = query_input
                        st.session_state.last_source_filter = source_filter

                        # Track query history
                        if "query_history" not in st.session_state:
                            st.session_state.query_history = []
                        if query_input not in st.session_state.query_history:
                            st.session_state.query_history.append(query_input)

                    elif response.status_code == 400:
                        st.error("❌ Bad Request (400): Check your query syntax")
                        with st.expander("View error response"):
                            st.text(response.text)
                    elif response.status_code == 500:
                        st.error("❌ Server Error (500): The backend encountered an error")
                        with st.expander("View error response"):
                            st.text(response.text)
                    else:
                        st.error(f"❌ HTTP Error {response.status_code}")
                        with st.expander("View error response"):
                            st.text(response.text)

                except requests.exceptions.ConnectionError:
                    st.error("❌ Connection Error: Cannot connect to the API server.")
                    st.info(f"💡 Make sure the backend is running on {config['api']['backend_url']}")
                except requests.exceptions.Timeout:
                    st.error("❌ Timeout Error: The API request took too long.")
                except Exception as e:
                    st.error(f"⚠️ Unexpected Error: {str(e)}")
                    logger.error(f"Query execution error: {e}", exc_info=True)

        # Display results if available
        if st.session_state.query_results is not None:
            st.markdown("---")
            self.display_results(st.session_state.query_results)

def main():
    try:
        app = InsuranceQueryApp()
        app.run()
    except Exception as e:
        st.error(f"❌ Application Error: {str(e)}")
        logger.error(f"Application error: {e}", exc_info=True)


if __name__ == "__main__":
    main()
