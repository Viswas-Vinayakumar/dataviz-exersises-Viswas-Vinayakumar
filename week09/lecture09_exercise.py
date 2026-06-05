"""
Lecture 9 Exercise — World Happiness Dashboard
================================================
Run with: streamlit run lecture09_exercise.py

Dashboard purpose (REQUIRED — write this before any code):
# PURPOSE: [one sentence: audience + what they can do with this dashboard]

BBD colour rule: name the colour type you use in a comment next to each chart:
# COLOUR TYPE: sequential / diverging / categorical / highlight
"""

import streamlit as st
import pandas as pd
import plotly.express as px

df = pd.read_csv('../data/world_happiness_2023.csv')
df.columns = ['Country','Region','Score','GDP','Social_Support',
              'Life_Expectancy','Freedom','Generosity','Corruption']

st.set_page_config(page_title="World Happiness Dashboard", page_icon="🌍", layout="wide")

# ─────────────────────────────────────────────────────────────────────────────
# TASK 1: Title and caption
# ─────────────────────────────────────────────────────────────────────────────
# YOUR CODE HERE


# ─────────────────────────────────────────────────────────────────────────────
# TASK 2: Sidebar filters
#   - st.selectbox for Region ('All' option)
#   - st.slider for top N countries (5-30, default 15)
# Filter the dataframe. Store as `filtered`.
# ─────────────────────────────────────────────────────────────────────────────
with st.sidebar:
    st.header("Filters")
    # YOUR CODE HERE

# filtered = ...


# ─────────────────────────────────────────────────────────────────────────────
# TASK 3: KPI row — 3 st.metric() cards
#   1. Number of countries shown
#   2. Average score (with delta vs global average)
#   3. Happiest country in current selection
# ─────────────────────────────────────────────────────────────────────────────
# YOUR CODE HERE


st.divider()

# ─────────────────────────────────────────────────────────────────────────────
# TASK 4: Two-column layout — two charts
#   Left (wider): horizontal bar of top N countries, sorted by score
#   Right: scatter of GDP vs Score
#
# BBD colour requirement:
#   - Name the colour type you chose (sequential/diverging/categorical/highlight)
#     in a comment next to the colour argument
#   - Do NOT use red and green as the only differentiator (CVD rule)
#
# SWD requirements:
#   - White background, Arial font
#   - Bar chart x-axis starts at 0
#   - Insight title (not topic title)
#   - use_container_width=True
# ─────────────────────────────────────────────────────────────────────────────
# YOUR CODE HERE


# ─────────────────────────────────────────────────────────────────────────────
# EXTENSION: Add a third chart of your choice using a DIVERGING colour scale
# (something where values go above and below a meaningful midpoint)
# Label the midpoint in an annotation.
# ─────────────────────────────────────────────────────────────────────────────
# YOUR CODE HERE (optional)
