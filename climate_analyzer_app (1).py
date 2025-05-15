import streamlit as st
import pandas as pd
import plotly.express as px
import requests
import json

# Set page configuration
st.set_page_config(page_title="Climate Data Analyzer", layout="wide")

# Page title
st.title("Climate Data Analyzer")
st.write("Upload climate data as CSV and get AI-powered insights and visualizations")

# API key input (in a real app, use secrets management)
with st.sidebar:
    st.header("Configuration")
    api_key = st.text_input("Anthropic API Key", type="password")
    
    st.subheader("About")
    st.write("""
    This app analyzes climate data using AI.
    Upload a CSV file containing climate metrics.
    """)

# Function to call Claude API directly via requests
def call_claude_api(api_key, prompt):
    headers = {
        "x-api-key": api_key,
        "anthropic-version": "2023-06-01",
        "content-type": "application/json"
    }
    
    data = {
        "model": "claude-3-7-sonnet-20250219",
        "messages": [
            {"role": "user", "content": prompt}
        ],
        "max_tokens": 1000,
        "temperature": 0
    }
    
    response = requests.post(
        "https://api.anthropic.com/v1/messages",
        headers=headers,
        json=data
    )
    
    if response.status_code == 200:
        return response.json()["content"][0]["text"]
    else:
        st.error(f"API Error: {response.status_code}")
        st.error(response.text)
        return None

# File uploader
uploaded_file = st.file_uploader("Upload your climate data (CSV format)", type="csv")

# Process the file when uploaded
if uploaded_file and api_key:
    # Read the CSV file
    df = pd.read_csv(uploaded_file)
    
    # Display the raw data
    st.subheader("Raw Data")
    st.dataframe(df)
    
    # Get first 5 rows as a string for AI context
    data_sample = df.head().to_string()
    column_info = "\n".join([f"- {col}: {df[col].dtype}" for col in df.columns])
    
    # Generate insights using Claude
    st.subheader("AI Analysis")
    
    with st.spinner("Analyzing data with AI..."):
        try:
            # Create a prompt for Claude
            prompt = f"""
            You are a climate data analyst. Analyze this climate dataset:
            
            Column information:
            {column_info}
            
            Data sample:
            {data_sample}
            
            Provide:
            1. 3-5 key insights from this data
            2. What visualization types would be most useful for this data
            3. Any data quality issues or limitations you notice
            
            Format your response clearly with markdown headings and bullet points.
            """
            
            # Call Claude API directly using requests
            completion = call_claude_api(api_key, prompt)
            
            if completion:
                # Display Claude's analysis
                st.markdown(completion)
        
        except Exception as e:
            st.error(f"Error with AI analysis: {str(e)}")
    
    # Automatic visualizations
    st.subheader("Visualizations")
    
    # If we have numeric columns, create visualizations
    numeric_cols = df.select_dtypes(include=['float64', 'int64']).columns.tolist()
    if len(numeric_cols) >= 2:
        # Let user select columns to visualize
        x_axis = st.selectbox("Select X-axis", options=df.columns)
        y_axis = st.selectbox("Select Y-axis", options=numeric_cols)
        
        # Create visualization
        fig = px.line(df, x=x_axis, y=y_axis, title=f"{y_axis} over {x_axis}")
        st.plotly_chart(fig, use_container_width=True)
        
        # If we have multiple numeric columns, offer a correlation heatmap
        if len(numeric_cols) > 2:
            st.subheader("Correlation Analysis")
            corr_matrix = df[numeric_cols].corr()
            fig_corr = px.imshow(corr_matrix, 
                               text_auto=True, 
                               title="Correlation Between Variables")
            st.plotly_chart(fig_corr, use_container_width=True)
else:
    if not api_key and uploaded_file:
        st.info("Please enter your Anthropic API key in the sidebar")
    elif not uploaded_file:
        st.info("Please upload a CSV file to begin analysis")