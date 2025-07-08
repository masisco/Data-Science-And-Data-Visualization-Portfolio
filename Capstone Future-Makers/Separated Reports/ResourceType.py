import streamlit as st
import pandas as pd
from datetime import datetime
import plotly.express as px
import seaborn as sns
import matplotlib.pyplot as plt

st.set_page_config(page_title="Account Engagement Report", layout="wide")
st.title("Account-Level Spark Engagement Report")

# Upload section
st.sidebar.header("Upload CSV Files")
access_logs_file = st.sidebar.file_uploader("Upload access_logs.csv", type=["csv"])
users_file = st.sidebar.file_uploader("Upload users.csv", type=["csv"])
organizations_file = st.sidebar.file_uploader("Upload organizations.csv", type=["csv"])

# Load static sparks file
sparks = pd.read_csv("sparks.csv")  # Ensure this file exists in your working directory

if access_logs_file and users_file and organizations_file:
    access_logs = pd.read_csv(access_logs_file)
    users = pd.read_csv(users_file)
    organizations = pd.read_csv(organizations_file)
    access_logs['Timestamp'] = pd.to_datetime(access_logs['Timestamp'])

    # Select an organization
    org_options = organizations[['Organization ID', 'Organization Name']].drop_duplicates()
    org_name = st.selectbox("Select an Account (Organization)", org_options['Organization Name'])
    org_id = org_options[org_options['Organization Name'] == org_name]['Organization ID'].values[0]

    # Filter users in selected organization
    org_users = users[users['Organization ID'] == org_id]
    
    # Show available date range in access logs
    min_date = access_logs['Timestamp'].min().date()
    max_date = access_logs['Timestamp'].max().date()
    st.markdown(f"🗓️ **Available Date Range in Access Logs:** {min_date} to {max_date}")


    # Date range filter
    start_date = st.date_input("Start Date", value=access_logs['Timestamp'].min().date())
    end_date = st.date_input("End Date", value=access_logs['Timestamp'].max().date())

    if start_date > end_date:
        st.error("Start date must be before end date.")
    else:
        # Filter logs for selected org users and date range
        filtered_logs = access_logs[
            (access_logs['User ID'].isin(org_users['User ID'])) &
            (access_logs['Timestamp'].dt.date >= start_date) &
            (access_logs['Timestamp'].dt.date <= end_date)
        ]

        st.subheader("Account Info")
        st.markdown(f"**Organization:** {org_name}")
        st.markdown(f"**Total Users:** {org_users.shape[0]}")

        # --- User List Table ---
        st.subheader("User List")
        user_list_df = org_users[['First Name', 'Last Name', 'User Email']].copy()
        user_list_df['Full Name'] = user_list_df['First Name'] + ' ' + user_list_df['Last Name']
        user_list_df = user_list_df[['Full Name', 'User Email']]
        st.dataframe(user_list_df)

        # --- Site List Table ---
        st.subheader("Site List")
        unique_sites = org_users[['Work Address']].dropna().drop_duplicates().reset_index(drop=True)
        unique_sites.index += 1
        unique_sites.columns = ['Site']
        st.dataframe(unique_sites)

        # Define resources
        resource_cols = ['Viewed Slideshow', 'Downloaded Slideshow', 'Watched Tutorial Video', 'Downloaded AI Playbook']

        # --- User Sessions per Spark ---
        user_sessions_per_spark = filtered_logs.groupby('Spark ID')['User ID'].nunique().reset_index()
        user_sessions_per_spark.rename(columns={'User ID': 'Sessions'}, inplace=True)
        user_sessions_per_spark = user_sessions_per_spark.merge(sparks[['Spark ID', 'Name']], on='Spark ID', how='left')
        user_sessions_per_spark.rename(columns={'Name': 'Spark Name'}, inplace=True)

        st.subheader("User Sessions per Spark")
        st.dataframe(user_sessions_per_spark[['Spark Name', 'Sessions']])

        # --- Spark Engagement Summary ---
        spark_summary = filtered_logs.groupby('Spark ID')[resource_cols + ['Access ID']].agg({
            **{col: 'sum' for col in resource_cols},
            'Access ID': 'nunique'
        }).reset_index()
        spark_summary['Total Resources Used'] = spark_summary[resource_cols].sum(axis=1)
        spark_summary['Percent Resources Used'] = (
            spark_summary['Total Resources Used'] / len(resource_cols)
        ).clip(upper=1) * 100
        spark_summary.rename(columns={'Access ID': 'Sessions'}, inplace=True)

        spark_summary = spark_summary.merge(sparks[['Spark ID', 'Name']], on='Spark ID', how='left')
        spark_summary.rename(columns={'Name': 'Spark Name'}, inplace=True)

        st.subheader("Spark Engagement Summary")
        st.dataframe(spark_summary[['Spark Name', 'Sessions', 'Percent Resources Used']])


        # --- Overall Resource Usage Pie Chart ---
        st.subheader("Overall Resource Usage Breakdown")

        # Sum each resource type across all Sparks
        total_resource_usage = filtered_logs[resource_cols].sum()

        # Create a pie chart
        fig_pie = px.pie(
            names=total_resource_usage.index,
            values=total_resource_usage.values,
            title="Distribution of Resource Interactions",
            color_discrete_sequence=px.colors.qualitative.Set3
        )
        st.plotly_chart(fig_pie)

        # --- Resource Usage per Spark  ---
        st.subheader("Resource Usage per Spark")

        # Prepare data
        resource_usage_data = filtered_logs.groupby('Spark ID')[resource_cols].sum().reset_index()
        resource_usage_data = resource_usage_data.merge(sparks[['Spark ID', 'Name']], on='Spark ID', how='left')
        resource_usage_data.set_index('Name', inplace=True)
        resource_usage_data = resource_usage_data[resource_cols]

        # Reset index for plotting
        resource_usage_reset = resource_usage_data.reset_index()

        # Melt the data for Seaborn compatibility
        melted_data = resource_usage_reset.melt(id_vars='Name', var_name='Resource Type', value_name='Interactions')

        # --- Bubble Chart (Scatter Plot) ---
        st.markdown("### Bubble Chart: Resource Interactions per Spark")
        fig_bubble, ax_bubble = plt.subplots(figsize=(12, 6))
        # Size of bubbles will be proportional to interactions (multiply to make them visible)
        sns.scatterplot(
            data=melted_data,
            x='Name',
            y='Resource Type',
            size='Interactions',
            hue='Interactions',
            sizes=(20, 300),  # min and max bubble sizes
            palette='coolwarm',
            legend=False,
            alpha=0.7
        )
        plt.xticks(rotation=45, ha='right')
        plt.title('Resource Interactions per Spark (Bubble Chart)')
        plt.xlabel('Spark Name')
        plt.ylabel('Resource Type')
        st.pyplot(fig_bubble)


else:
    st.info("Please upload access_logs, users, and organizations CSV files to begin.")
