import streamlit as st
import pandas as pd
import plotly.express as px
import anthropic

# --- Streamlit App Setup ---
st.set_page_config(page_title="Climate Data Analyzer", layout="wide")
st.title("🌍 Climate Data Analyzer")
st.markdown("Upload your climate CSV file and analyze trends using visualizations and AI-powered summaries.")

# --- File Upload ---
uploaded_file = st.file_uploader("Upload a climate data CSV file", type="csv")

if uploaded_file:
    try:
        df = pd.read_csv(uploaded_file)
        st.success("CSV file loaded successfully.")
    except Exception as e:
        st.error(f"Error loading CSV: {e}")
        st.stop()
else:
    st.info("No file uploaded. Using default sample dataset.")
    from io import StringIO

    sample_data = StringIO("""
date,temperature_c,precipitation_mm,humidity_percent,co2_ppm,sea_level_change_mm
2000-01-01,14.2,78.3,67,369.52,0
2001-01-01,14.3,82.1,68,371.13,2.5
2002-01-01,14.5,79.5,67,373.22,4.8
2003-01-01,14.6,81.2,69,375.77,7.2
2004-01-01,14.4,83.7,68,377.49,9.6
2005-01-01,14.7,77.9,65,379.80,12.1
2006-01-01,14.9,75.3,66,381.90,14.5
2007-01-01,14.8,79.8,67,383.76,16.8
2008-01-01,14.6,84.2,68,385.59,19.2
2009-01-01,14.9,76.5,65,387.38,21.5
2010-01-01,15.0,74.8,66,389.85,23.9
2011-01-01,14.9,82.1,67,391.63,26.2
2012-01-01,15.1,79.3,66,393.82,28.6
2013-01-01,15.0,81.5,68,396.48,31.0
2014-01-01,15.2,78.4,67,398.65,33.3
2015-01-01,15.5,76.2,65,400.83,35.7
2016-01-01,15.7,73.9,64,404.21,38.0
2017-01-01,15.6,77.5,66,406.55,40.4
2018-01-01,15.8,79.8,67,408.52,42.8
2019-01-01,15.9,74.6,65,411.44,45.1
2020-01-01,16.1,71.2,64,414.24,47.5
2021-01-01,16.0,76.8,66,416.96,49.8
2022-01-01,16.2,73.5,65,419.48,52.2
2023-01-01,16.4,69.8,63,422.31,54.6
2024-01-01,16.5,72.3,64,425.12,57.0
""")
    df = pd.read_csv(sample_data)
    st.success("Sample dataset loaded.")

# --- Convert 'date' column to datetime ---
df['date'] = pd.to_datetime(df['date'])

# --- Line Charts ---
st.subheader("📈 Climate Trends")
metrics = ['temperature_c', 'precipitation_mm', 'humidity_percent', 'co2_ppm', 'sea_level_change_mm']
for metric in metrics:
    fig = px.line(df, x='date', y=metric, title=f"{metric.replace('_', ' ').title()} Over Time")
    st.plotly_chart(fig, use_container_width=True)

# --- AI Analysis Section ---
st.subheader("🤖 AI Climate Insight")

api_key = st.text_input("Enter your Anthropic API Key", type="password")
if api_key and st.button("Generate Insight"):
    prompt_text = (
        "Analyze the following climate data trends and provide insights about long-term climate changes:\n\n"
        + df.tail(10).to_string(index=False)
    )

    try:
        client = anthropic.Client(api_key=api_key)
        response = client.completions.create(
            model="claude-v1",
            prompt=f"{anthropic.HUMAN_PROMPT} {prompt_text}{anthropic.AI_PROMPT}",
            max_tokens_to_sample=300
        )
        st.success("AI-generated summary:")
        st.write(response.completion.strip())
    except Exception as e:
        st.error(f"Error with AI analysis: {e}")
