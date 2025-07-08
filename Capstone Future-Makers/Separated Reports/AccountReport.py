import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import datetime

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

    # Date range filter
    min_date = access_logs['Timestamp'].min().date()
    max_date = access_logs['Timestamp'].max().date()
    st.markdown(f"**Selectable Date Range:** {min_date} to {max_date}")

    start_date = st.date_input("Start Date", value=min_date, min_value=min_date, max_value=max_date)
    end_date = st.date_input("End Date", value=max_date, min_value=min_date, max_value=max_date)

    if start_date > end_date:
        st.error("Start date must be before end date.")
    else:
        # Filter logs for selected org users and date range
        filtered_logs = access_logs[
            (access_logs['User ID'].isin(org_users['User ID'])) &
            (access_logs['Timestamp'].dt.date >= start_date) &
            (access_logs['Timestamp'].dt.date <= end_date)
        ]

        # --- Account Info ---
        st.subheader("Account Info")
        st.markdown(f"**Organization:** {org_name}")
        st.markdown(f"**Total Users:** {org_users.shape[0]}")

        # --- User List ---
        st.subheader("User List")
        user_list_df = org_users[['First Name', 'Last Name', 'User Email']].copy()
        user_list_df['Full Name'] = user_list_df['First Name'] + ' ' + user_list_df['Last Name']
        user_table = user_list_df[['Full Name', 'User Email']].sort_values(by='Full Name')
        st.dataframe(user_table.reset_index(drop=True))

        # --- Site List ---
        st.subheader("Site List")
        unique_sites = org_users['Work Address'].dropna().unique()
        if len(unique_sites) > 0:
            site_table = pd.DataFrame(sorted(unique_sites), columns=['Work Address'])
            st.dataframe(site_table.reset_index(drop=True))
        else:
            st.write("No site information available.")

        # Define resource interaction columns
        resource_cols = [
            'Viewed Slideshow',
            'Downloaded Slideshow',
            'Watched Tutorial Video',
            'Downloaded AI Playbook',
            'Accessed Extension Activities',
            'Used AI Playbook Maker',
            'Booked Support Session'
        ]

        # --- Sparks Accessed in Date Range ---
        accessed_sparks = filtered_logs['Spark ID'].dropna().unique()
        accessed_spark_names = sparks[sparks['Spark ID'].isin(accessed_sparks)][['Spark ID', 'Name']].rename(columns={'Name': 'Spark Name'})

        st.subheader("Sparks Accessed in Date Range")
        if not accessed_spark_names.empty:
            st.dataframe(accessed_spark_names.sort_values('Spark Name').reset_index(drop=True))
        else:
            st.write("No Sparks accessed during the selected date range.")

        # --- Percent of Resources Accessed per Spark ---
        spark_resource_usage = filtered_logs.groupby('Spark ID')[resource_cols].agg('sum').reset_index()
        spark_resource_usage['Resources Accessed'] = (spark_resource_usage[resource_cols] > 0).sum(axis=1)
        spark_resource_usage['Percent Resources Accessed'] = (
            spark_resource_usage['Resources Accessed'] / len(resource_cols)
        ) * 100
        spark_resource_usage = spark_resource_usage.merge(sparks[['Spark ID', 'Name']], on='Spark ID', how='left')
        spark_resource_usage.rename(columns={'Name': 'Spark Name'}, inplace=True)

        st.subheader("Percent of Resources Accessed Per Spark")
        st.dataframe(spark_resource_usage[['Spark Name', 'Percent Resources Accessed']])

        # --- User Sessions per Spark ---
        spark_sessions = filtered_logs.groupby('Spark ID')['Access ID'].nunique().reset_index()
        spark_sessions.rename(columns={'Access ID': 'User Sessions'}, inplace=True)
        spark_sessions = spark_sessions.merge(sparks[['Spark ID', 'Name']], on='Spark ID', how='left')
        spark_sessions.rename(columns={'Name': 'Spark Name'}, inplace=True)

        st.subheader("Number of User Sessions per Spark")
        st.dataframe(spark_sessions[['Spark Name', 'User Sessions']])

        # --- Combined Spark Summary ---
        spark_summary = filtered_logs.groupby([filtered_logs['Timestamp'].dt.date, 'Spark ID'])[resource_cols + ['Access ID']].agg({ **{col: 'sum' for col in resource_cols}, 'Access ID': 'nunique'}).reset_index()
        spark_summary['Total Resources Used'] = spark_summary[resource_cols].sum(axis=1)
        spark_summary['Percent Resources Used'] = ( spark_summary['Total Resources Used'] / len(resource_cols)).clip(upper=1) * 100
        spark_summary.rename(columns={'Access ID': 'User Sessions'}, inplace=True)
        spark_summary = spark_summary.merge(sparks[['Spark ID', 'Name']], on='Spark ID', how='left')
        spark_summary.rename(columns={'Name': 'Spark Name'}, inplace=True)
        st.subheader("Spark Engagement Summary")
        st.dataframe(spark_summary[['Spark Name', 'User Sessions', 'Percent Resources Used', 'Timestamp']])


        # --- Graph 1: Total Resources Accessed per Spark ---
        resource_usage_per_spark = spark_resource_usage[['Spark Name', 'Percent Resources Accessed']]
        fig1 = px.bar(
            resource_usage_per_spark,
            x='Spark Name',
            y='Percent Resources Accessed',
            title="Percent of Resources Accessed per Spark",
            labels={'Percent Resources Accessed': 'Percentage of Resources Accessed'},
            color='Percent Resources Accessed',
            color_continuous_scale=["gold", "orange",
                                    "red"]
        )
        fig1.update_layout(xaxis_title='Spark', yaxis_title='Percentage of Resources Accessed', height=600)
        st.plotly_chart(fig1)

        # --- Graph 2: Session Length Distribution per Spark ---
        session_lengths = filtered_logs[['Spark ID', 'Session Length (min)']].dropna()
        session_lengths = session_lengths.merge(sparks[['Spark ID', 'Name']], on='Spark ID', how='left')

        fig2 = px.box(
            session_lengths,
            x='Name',
            y='Session Length (min)',
            title="Session Length Distribution per Spark",
            labels={'Session Length (min)': 'Session Length (minutes)', 'Name': 'Spark Name'},
            color='Name'
        )

        # Update layout and box plot line thickness
        fig2.update_layout(
            xaxis_title='Spark',
            yaxis_title='Session Length (min)',
            height=600
        )

        # Set the line thickness for the boxplot
        fig2.update_traces(
            line=dict(width=10)  # Adjust the width value to increase or decrease thickness
        ) # Adjust the width value to increase or decrease thickness

        st.plotly_chart(fig2)

else:
    st.info("Please upload access_logs, users, and organizations CSV files to begin.")