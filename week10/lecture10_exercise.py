
import datetime

import streamlit as st
import pandas as pd
import plotly.express as px
from pathlib import Path

st.set_page_config(page_title="CO2 Dashboard", page_icon="🌱", layout="wide")

# ── Data ──────────────────────────────────────────────────────────────────────
# @st.cache_data: Streamlit reruns the entire script on every widget interaction.
# Without caching, the CSV is read from disk on every interaction — slow and wasteful.
# cache_data stores the result after the first run and reuses it until the file changes.
@st.cache_data
def load_data():
    path = Path(__file__).parent.parent / 'data' / 'co2_emissions.csv'
    df = pd.read_csv(path)
    df['Date'] = pd.to_datetime(df['Year'].astype(str) + '-01-01')
    return df

df = load_data()

st.title("🌱 CO2 Emissions Explorer")
st.caption("Source: Our World in Data — ourworldindata.org/co2-emissions")

# ── TASK 1: Sidebar with 5 widgets ────────────────────────────────────────────
#   a) st.selectbox for Region (with 'All')
#   b) st.multiselect for Countries (updates based on region — chained)
#   c) st.date_input for date range (two-handle; convert years to Jan-1 dates)
#   d) st.radio for Metric: "Total CO2 (Mt)" vs "CO2 per capita"
#   e) st.checkbox labelled "Show only top emitter highlighted"
#
# Guards:
#   - empty countries → st.warning + st.stop()
#   - incomplete date_input → st.warning + st.stop()
# Convert date_input result to pd.Timestamp before filtering.
# ─────────────────────────────────────────────────────────────────────────────
min_year, max_year = int(df['Year'].min()), int(df['Year'].max())

with st.sidebar:
    st.header("Filters")

    # a) Region — selectbox for a single exclusive choice out of a longer list
    regions = ['All'] + sorted(df['Region'].unique())
    selected_region = st.selectbox("Region", regions)

    # b) Countries — chained off Region, so the list only ever offers valid options
    if selected_region == 'All':
        country_options = sorted(df['Country'].unique())
    else:
        country_options = sorted(df.loc[df['Region'] == selected_region, 'Country'].unique())

    selected_countries = st.multiselect("Countries", country_options,
                                        default=country_options[:4])

    # c) Date range — the loader turned integer years into Jan-1 timestamps,
    #    so the calendar picker works on real dates
    date_range = st.date_input(
        "Date range",
        value=(datetime.date(2005, 1, 1), datetime.date(max_year, 1, 1)),
        min_value=datetime.date(min_year, 1, 1),
        max_value=datetime.date(max_year, 1, 1),
        format="YYYY-MM-DD",
    )

    st.divider()

    # d) Metric — radio, because two mutually exclusive options should both be visible
    metric = st.radio("Metric", ["Total CO2 (Mt)", "CO2 per capita"])

    # e) Grey-and-highlight toggle
    highlight_top = st.checkbox("Show only top emitter highlighted")

# Guard: multiselect returns [] when nothing is selected
if not selected_countries:
    st.warning("Select at least one country.")
    st.stop()

# Guard: date_input returns a 1-tuple while the user has clicked start but not end
if len(date_range) != 2:
    st.warning("Select a start AND end date.")
    st.stop()

# Always convert date → pd.Timestamp before comparing against a datetime64 column
start_ts, end_ts = pd.Timestamp(date_range[0]), pd.Timestamp(date_range[1])

filtered = df[
    df['Country'].isin(selected_countries) &
    (df['Date'] >= start_ts) &
    (df['Date'] <= end_ts)
]

if filtered.empty:
    st.warning("No data in this date range for the selected countries.")
    st.stop()

y_col = 'CO2_Mt' if metric == "Total CO2 (Mt)" else 'CO2_per_capita'
y_label = 'CO2 Emissions (Mt)' if y_col == 'CO2_Mt' else 'CO2 per Capita (t)'

# Reserve the KPI row here so it renders above the charts (filled in at the bottom)
kpi_row = st.container()

# ── TASK 2: Filter summary caption ────────────────────────────────────────────
# Show: "X countries | Region | Date range | Metric"
# BBD rule: always show users how many records match current filters
# ─────────────────────────────────────────────────────────────────────────────
st.caption(
    f"{len(selected_countries)} countries | {selected_region} | "
    f"{date_range[0].strftime('%d %b %Y')} — {date_range[1].strftime('%d %b %Y')} | "
    f"{metric} | {len(filtered)} records match"
)

# ── TASK 3: Two charts reacting to ALL filters ────────────────────────────────
#   Left: line chart — selected metric over time, one line per country
#         If "Show only top emitter highlighted" checkbox is on:
#           - grey all lines except the highest emitter in the date range
#           - label that country at the end of its line (SWD grey-and-highlight)
#   Right: bar chart — ranking for the last year in selected date range
#
# BBD colour requirement: name the colour type in a comment next to each chart
# SWD requirements: white background, insight title, use_container_width=True
# ─────────────────────────────────────────────────────────────────────────────
last_year = int(filtered['Year'].max())
first_year = int(filtered['Year'].min())
last_year_data = filtered[filtered['Year'] == last_year]

# The top emitter is ranked on total emissions across the whole selected range
range_totals = filtered.groupby('Country')[y_col].sum()
top_country = range_totals.idxmax()

col_left, col_right = st.columns([2, 1])

with col_left:
    # Line chart
    if highlight_top:
        # COLOUR TYPE: accent (grey-and-highlight) — one series carries the message,
        # every other country drops to grey context.
        colour_map = {c: '#D9D9D9' for c in selected_countries}
        colour_map[top_country] = '#2E75B6'
        title = f'{top_country} dominates {metric.lower()} across {first_year}–{last_year}'
    else:
        # COLOUR TYPE: categorical (qualitative) — colour only separates countries,
        # it carries no magnitude. Safe is a CVD-safe qualitative palette.
        colour_map = dict(zip(selected_countries, px.colors.qualitative.Safe))
        title = f'{metric} by country, {first_year}–{last_year}'

    fig1 = px.line(
        filtered,
        x='Date',
        y=y_col,
        color='Country',
        color_discrete_map=colour_map,
        labels={y_col: y_label, 'Date': ''},
        title=title,
    )
    fig1.update_layout(plot_bgcolor='white', paper_bgcolor='white',
                       font=dict(family='Arial'),
                       yaxis=dict(gridcolor='#F0F0F0'))

    if highlight_top:
        # Direct label beats a legend when only one series matters
        fig1.update_traces(line=dict(width=1.5))
        fig1.update_traces(selector=dict(name=top_country), line=dict(width=3))
        end_point = (filtered[filtered['Country'] == top_country]
                     .sort_values('Date').iloc[-1])
        fig1.add_annotation(
            x=end_point['Date'], y=end_point[y_col], text=f" {top_country}",
            showarrow=False, xanchor='left', font=dict(color='#2E75B6', size=12),
        )
        fig1.update_layout(showlegend=False, margin=dict(r=90))

    # width='stretch' is the Streamlit 1.51 replacement for use_container_width=True
    st.plotly_chart(fig1, width='stretch')

with col_right:
    # Bar chart
    # COLOUR TYPE: single accent hue — bar length already encodes the value, so a
    # second colour dimension would be redundant. The top emitter keeps the accent.
    ranking = last_year_data.sort_values(y_col)
    bar_colours = ['#2E75B6' if c == top_country else '#BFBFBF'
                   for c in ranking['Country']]

    fig2 = px.bar(
        ranking,
        x=y_col,
        y='Country',
        orientation='h',
        labels={y_col: y_label, 'Country': ''},
        title=f'{last_year} ranking — {top_country} leads',
    )
    fig2.update_traces(marker_color=bar_colours, marker_line_width=0)
    fig2.update_layout(plot_bgcolor='white', paper_bgcolor='white',
                       font=dict(family='Arial'),
                       xaxis=dict(range=[0, ranking[y_col].max() * 1.15],
                                  gridcolor='#F0F0F0'))
    st.plotly_chart(fig2, width='stretch')

# ── EXTENSION: KPI row above the charts ───────────────────────────────────────
#   - Total CO2 in last year of selected range (sum across selected countries)
#   - % change from first to last year
#   - Country with highest emissions in last year
# ─────────────────────────────────────────────────────────────────────────────
# Totals only add up for absolute emissions — per-capita rates have to be averaged,
# because summing rates across countries produces a number that means nothing
aggregate = 'sum' if y_col == 'CO2_Mt' else 'mean'
kpi_label = metric if aggregate == 'sum' else f"Average {metric}"

first_year_value = filtered.loc[filtered['Year'] == first_year, y_col].agg(aggregate)
last_year_value = last_year_data[y_col].agg(aggregate)
pct_change = ((last_year_value - first_year_value) / first_year_value * 100
              if first_year_value else 0)
biggest = last_year_data.loc[last_year_data[y_col].idxmax()]

with kpi_row:
    kpi1, kpi2, kpi3 = st.columns(3)
    kpi1.metric(f"{kpi_label}, {last_year}", f"{last_year_value:,.1f}")
    kpi2.metric(f"Change {first_year} → {last_year}", f"{pct_change:+.1f}%",
                delta=f"{last_year_value - first_year_value:+,.1f}")
    kpi3.metric(f"Highest in {last_year}", biggest['Country'],
                delta=f"{biggest[y_col]:,.1f}", delta_color="off")
