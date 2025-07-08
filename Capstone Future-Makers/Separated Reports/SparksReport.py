import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import datetime

st.set_page_config(page_title="Spark Engagement Report", layout="wide")
st.title("Spark Engagement Report Generator")

# Upload section
st.sidebar.header("Upload CSV Files")
access_logs_file = st.sidebar.file_uploader("Upload access_logs.csv", type=["csv"])
users_file = st.sidebar.file_uploader("Upload users.csv", type=["csv"])
sparks_file = st.sidebar.file_uploader("Upload sparks.csv", type=["csv"])
organizations_file = st.sidebar.file_uploader("Upload organizations.csv", type=["csv"])

# Check if all files are uploaded
if access_logs_file and users_file and sparks_file and organizations_file:
    access_logs = pd.read_csv(access_logs_file)
    users = pd.read_csv(users_file)
    sparks = pd.read_csv(sparks_file)
    organizations = pd.read_csv(organizations_file)

    # Convert Timestamp to datetime
    access_logs['Timestamp'] = pd.to_datetime(access_logs['Timestamp'])

    # Ask user to select organization and date range
    selected_org = st.selectbox("Select Organization", organizations['Organization Name'].unique())
    start_date = st.date_input("Start Date", value=access_logs['Timestamp'].min().date())
    end_date = st.date_input("End Date", value=access_logs['Timestamp'].max().date())

    if start_date > end_date:
        st.error("Start date must be before end date.")
    else:
        # Filter by date and organization
        org_users = users[users['Organization ID'].isin(organizations[organizations['Organization Name'] == selected_org]['Organization ID'])]
        filtered_logs = access_logs[
            (access_logs['User ID'].isin(org_users['User ID'])) &
            (access_logs['Timestamp'].dt.date >= start_date) &
            (access_logs['Timestamp'].dt.date <= end_date)
        ]

        # Sessions per Spark
        sessions_per_spark = filtered_logs.groupby('Spark ID')['Access ID'].nunique().reset_index()
        sessions_per_spark = sessions_per_spark.merge(sparks, left_on='Spark ID', right_on='Spark ID', how='left')
        sessions_per_spark.rename(columns={'Access ID': 'Sessions', 'Name': 'Spark Name'}, inplace=True)
        st.subheader("Sessions per Spark")
        st.dataframe(sessions_per_spark[['Spark Name', 'Sessions']])

        # Percentage of resources accessed per Spark
        resource_cols = ['Viewed Slideshow', 'Downloaded Slideshow', 'Watched Tutorial Video', 'Downloaded AI Playbook']
        spark_resource_usage = filtered_logs.groupby('Spark ID')[resource_cols].sum().reset_index()
        spark_resource_usage['Total'] = spark_resource_usage[resource_cols].sum(axis=1)
        spark_resource_usage['Percent Used'] = (spark_resource_usage['Total'] / (len(resource_cols) * filtered_logs.groupby('Spark ID').size())).fillna(0) * 100
        spark_resource_usage = spark_resource_usage.merge(sparks, left_on='Spark ID', right_on='Spark ID', how='left')
        st.subheader("Percentage of Resources Accessed per Spark")
        st.dataframe(spark_resource_usage[['Name', 'Percent Used']].rename(columns={'Name': 'Spark Name'}))

        # Accounts and Sites associated
        associated_org_id = organizations[organizations['Organization Name'] == selected_org]['Organization ID'].values[0]
        associated_sites = org_users['Work Address'].dropna().unique()
        st.subheader("Accounts and Sites Associated")
        st.markdown(f"**Organization:** {selected_org} (ID: {associated_org_id})")
        st.markdown(f"**Sites:** {', '.join(associated_sites.astype(str)) if len(associated_sites) > 0 else 'None'}")

        # Users Associated
        st.subheader("Users Associated")
        user_list = org_users[['First Name', 'Last Name', 'User Email']].copy()
        user_list['Name'] = user_list['First Name'] + ' ' + user_list['Last Name']
        st.dataframe(user_list[['Name', 'User Email']].rename(columns={'User Email': 'Email'}))

        # --- Graph 1: Bubble Chart - Top Sparks by Sessions and Resources Accessed ---
        st.subheader("Top Sparks by Sessions and Engagement")

        top_sparks = sessions_per_spark.sort_values(by='Sessions', ascending=False).head(10)  # top 10
        top_sparks = top_sparks.merge(
            spark_resource_usage[['Spark ID', 'Percent Used']],
            on='Spark ID',
            how='left'
        )

        if not top_sparks.empty:
            fig1 = px.scatter(
                top_sparks,
                x='Sessions',
                y='Percent Used',
                size='Sessions',
                color='Spark Name',
                hover_name='Spark Name',
                size_max=60,
                title="Top Sparks by Sessions and Resource Engagement",
            )

            fig1.update_layout(
                xaxis_title="Number of Sessions",
                yaxis_title="Percent of Resources Accessed",
                height=600,
            )

            st.plotly_chart(fig1)
        else:
            st.info("No session data available to display.")

        # --- Graph 2: Bar Chart with Colorful Bars and Horizontal Labels ---
        st.subheader("Overall Resource Access Rates")

        total_resources_accessed = filtered_logs[resource_cols].sum().sort_values(ascending=True)

        if not total_resources_accessed.empty:
            fig2 = px.bar(
                total_resources_accessed,
                x=total_resources_accessed.index,
                y=total_resources_accessed.values,
                color=total_resources_accessed.index,
                title="Overall Resource Access Rates"
            )

            fig2.update_layout(
                xaxis_title="Resource Type",
                yaxis_title="Total Accesses",
                xaxis_tickangle=0,  # <-- Horizontal labels
                height=500,
                showlegend=False,
            )

            st.plotly_chart(fig2)
        else:
            st.info("No resource access data available to display.")

        # --- Graph 3: Sessions Over Time (unchanged) ---
        st.subheader("Sessions Over Time")

        sessions_over_time = filtered_logs.copy()
        sessions_over_time['Date'] = sessions_over_time['Timestamp'].dt.date

        sessions_by_date = sessions_over_time.groupby('Date').size().reset_index(name='Sessions')

        if not sessions_by_date.empty:
            st.line_chart(sessions_by_date.set_index('Date')['Sessions'])
        else:
            st.info("No session activity data for the selected period.")

else:
    st.info("Please upload all required CSV files to begin.")
