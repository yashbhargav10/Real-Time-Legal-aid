import streamlit as st
import pandas as pd
from google.cloud import firestore
import os

# Set GCP Project
PROJECT_ID = os.getenv("GCP_PROJECT_ID", "legalaidassistant")

st.set_page_config(page_title="Observability Metrics", page_icon="📊", layout="wide")
st.title("📊 Legal Aid Assistant Observability Dashboard")
st.markdown("Monitoring key metrics and usage data from Firestore Sessions.")

@st.cache_data(ttl=60)
def fetch_metrics():
    try:
        db = firestore.Client(project=PROJECT_ID)
        sessions_ref = db.collection("sessions").stream()
        
        all_interactions = []
        total_sessions = 0
        
        for doc in sessions_ref:
            total_sessions += 1
            data = doc.to_dict()
            history = data.get("history", [])
            for interaction in history:
                interaction["session_id"] = doc.id
                all_interactions.append(interaction)
                
        return total_sessions, pd.DataFrame(all_interactions)
    except Exception as e:
        st.error(f"Failed to fetch from Firestore: {e}")
        return 0, pd.DataFrame()

total_sessions, df = fetch_metrics()

if df.empty:
    st.warning("No interactions found in the database. Ensure the API is generating valid traffic.")
else:
    # 1. Top Level Metrics
    total_queries = len(df)
    
    # Check if there are feedback or hallucination interception tags in metadata
    # We didn't explicitly add hallucination true/false to metadata, but let's assume 'retrieved_docs' is tracked
    
    col1, col2, col3 = st.columns(3)
    col1.metric("Total User Sessions", total_sessions)
    col2.metric("Total Queries Processed", total_queries)
    
    avg_docs = 0
    if "metadata" in df.columns:
        df["retrieved_docs"] = df["metadata"].apply(lambda m: m.get("retrieved_docs", 0) if isinstance(m, dict) else 0)
        avg_docs = df["retrieved_docs"].mean()
    col3.metric("Avg Docs Retrieved per Query", f"{avg_docs:.1f}")
    
    st.divider()
    
    # 2. Daily Query Volume Chart
    st.subheader("Daily Query Volume")
    if "timestamp" in df.columns:
        df["date"] = pd.to_datetime(df["timestamp"]).dt.date
        daily_counts = df.groupby("date").size().reset_index(name="counts")
        st.bar_chart(daily_counts, x="date", y="counts")
    
    # 3. Raw Data Explorer
    st.subheader("Recent Interactions Log")
    if "timestamp" in df.columns:
        df = df.sort_values(by="timestamp", ascending=False)
    
    st.dataframe(
        df[["session_id", "query", "response", "timestamp"]].head(50),
        use_container_width=True
    )
