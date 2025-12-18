import streamlit as st
import pandas as pd
import os
from crewai import Agent, Task, Crew, Process
from crewai_tools import SerperDevTool, ScrapeWebsiteTool

# 1. SETUP PAGE CONFIG
st.set_page_config(page_title="AI Sales Agent", page_icon="🚀")

st.title("🚀 AI Sales Outreach Generator")
st.write("Upload a CSV with 'company' and 'url' columns. The AI will research them and write emails.")

# 2. API KEYS (For production, we usually use secrets, but this works for now)
os.environ["OPENAI_API_KEY"] = "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" # <--- PASTE KEY
os.environ["SERPER_API_KEY"] = "065a377d583fc9ae6f8f6bce0788738b87e15d9f" # <--- PASTE KEY

# 3. DEFINE THE AGENT LOGIC (Cached to run faster)
def run_crew_logic(company, url):
    search_tool = SerperDevTool()
    scrape_tool = ScrapeWebsiteTool()

    researcher = Agent(
        role='Lead Researcher',
        goal='Find relevant news and pain points.',
        backstory="Expert researcher finding sales hooks.",
        tools=[search_tool, scrape_tool],
        verbose=False,
        memory=False # Disabled for speed in UI
    )

    writer = Agent(
        role='Email Copywriter',
        goal='Write personalized cold emails.',
        backstory="Top-tier copywriter. Short, punchy, problem-focused.",
        verbose=False,
        memory=False
    )

    research_task = Task(
        description=f"Research {company} ({url}). Find 2 news items and 1 pain point.",
        expected_output='Summary of hooks.',
        agent=researcher
    )

    email_task = Task(
        description=f"Write a cold email to a VP at {company} using the research. Max 150 words.",
        expected_output='Final email draft.',
        agent=writer
    )

    crew = Crew(
        agents=[researcher, writer],
        tasks=[research_task, email_task],
        process=Process.sequential
    )
    
    return str(crew.kickoff())

# 4. THE UI LOGIC
uploaded_file = st.file_uploader("Choose a CSV file", type="csv")

if uploaded_file is not None:
    df = pd.read_csv(uploaded_file)
    
    # Check if columns exist
    if 'company' not in df.columns or 'url' not in df.columns:
        st.error("CSV must have columns named 'company' and 'url'")
    else:
        if st.button("Start Agents"):
            st.info("Agents are working... this may take a few minutes.")
            
            # Create a progress bar
            progress_bar = st.progress(0)
            results = []
            
            # Loop through rows
            for index, row in df.iterrows():
                with st.spinner(f"Researching {row['company']}..."):
                    try:
                        email = run_crew_logic(row['company'], row['url'])
                    except Exception as e:
                        email = f"Error: {e}"
                
                results.append(email)
                # Update progress
                progress_bar.progress((index + 1) / len(df))
            
            # Add results to dataframe
            df['generated_email'] = results
            
            st.success("Done!")
            
            # Show preview
            st.dataframe(df)
            
            # Download button
            csv = df.to_csv(index=False).encode('utf-8')
            st.download_button(
                "Download Results CSV",
                csv,
                "ai_outreach_results.csv",
                "text/csv",
                key='download-csv'
            )