import streamlit as st
import pandas as pd
import plotly.express as px

DAY_ORDER = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']

@st.cache_data
def load_and_clean_data(file):
    df = pd.read_csv(file)
    df.columns = df.columns.str.strip()
    df = df.rename(columns={
        "Likes/Reactions": "likes",
        "Comments": "comments",
        "Shares/Retweets": "shares",
        "Post Timestamp": "date",
        "Platform": "platform",
        "Post Text": "post_text",
        "Media Type": "post_type"
    })
    df[["likes", "comments", "shares"]] = df[["likes", "comments", "shares"]].apply(pd.to_numeric, errors='coerce')
    df = df.dropna(subset=["likes", "comments", "shares", "date", "platform", "post_type"])
    df["date"] = pd.to_datetime(df["date"])
    df["day"] = df["date"].dt.day_name()
    df['day'] = pd.Categorical(df['day'], categories=DAY_ORDER, ordered=True)
    return df

def create_visualizations(df):
    agg_post_type = df.groupby("post_type")[["likes", "comments", "shares"]].sum().reset_index()
    fig1 = px.bar(agg_post_type.melt(id_vars="post_type", var_name="metric", value_name="count"),
                  x="post_type", y="count", color="metric", title="Total Engagement by Post Type",
                  labels={"count": "Total Engagement", "post_type": "Post Type"}, barmode="group")

    daily_engagement = df.groupby("date")[["likes", "comments", "shares"]].sum().reset_index()
    fig2 = px.line(daily_engagement.melt(id_vars="date", var_name="metric", value_name="count"),
                   x="date", y="count", color="metric", title="Daily Engagement Trend",
                   labels={"count": "Engagement Count", "date": "Date"}, markers=True)

    fig3 = px.box(df, x="day", y="likes", title="Likes Distribution by Day of Week",
                  labels={"likes": "Likes Count", "day": "Day of Week"},
                  color="day", category_orders={"day": DAY_ORDER})

    platform_engagement = df.groupby("platform")[["likes", "comments", "shares"]].sum().reset_index()
    fig4 = px.bar(platform_engagement.melt(id_vars="platform", var_name="metric", value_name="count"),
                  x="platform", y="count", color="metric", title="Engagement by Platform",
                  labels={"count": "Total Engagement", "platform": "Platform"}, barmode="group")
    
    return fig1, fig2, fig3, fig4

st.title("📊 Social Media Engagement Tracker")
uploaded_file = st.file_uploader("Upload Social Media CSV", type="csv")

if uploaded_file is not None:
    df = load_and_clean_data(uploaded_file)
    fig1, fig2, fig3, fig4 = create_visualizations(df)
    
    st.plotly_chart(fig1, use_container_width=True)
    st.plotly_chart(fig2, use_container_width=True)
    st.plotly_chart(fig3, use_container_width=True)
    st.plotly_chart(fig4, use_container_width=True)
