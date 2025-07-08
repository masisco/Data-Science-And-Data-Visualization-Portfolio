import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import datetime

st.set_page_config(page_title="Site Report", layout="wide")
st.title("Site Engagement Report Generator")

# Sidebar upload
st.sidebar.header("Upload CSV Files")
access_logs_file = st.sidebar.file_uploader("Upload access_logs.csv", type=["csv"])
users_file = st.sidebar.file_uploader("Upload users.csv", type=["csv"])
organizations_file = st.sidebar.file_uploader("Upload organizations.csv", type=["csv"])
sparks = pd.read_csv("sparks.csv")  # Static sparks file

if access_logs_file and users_file and organizations_file:
    # Load data
    access_logs = pd.read_csv(access_logs_file)
    users = pd.read_csv(users_file)
    organizations = pd.read_csv(organizations_file)

    # Convert timestamp
    access_logs['Timestamp'] = pd.to_datetime(access_logs['Timestamp'])

    # Select organization & date range
    selected_org = st.selectbox("Select Organization", organizations['Organization Name'].unique())
    start_date = st.date_input("Start Date", value=access_logs['Timestamp'].min().date())
    end_date = st.date_input("End Date", value=access_logs['Timestamp'].max().date())

    if start_date > end_date:
        st.error("Start date must be before end date.")
    else:
        org_id = organizations[organizations['Organization Name'] == selected_org]['Organization ID'].values[0]
        org_users = users[users['Organization ID'] == org_id]
        filtered_logs = access_logs[
            (access_logs['User ID'].isin(org_users['User ID'])) &
            (access_logs['Timestamp'].dt.date >= start_date) &
            (access_logs['Timestamp'].dt.date <= end_date)
        ]

        ### Number of Users
        unique_users = org_users[org_users['User ID'].isin(filtered_logs['User ID'])]

        st.subheader(" Site Summary")
        st.markdown(f"- **Total Users (active in range)**: {unique_users['User ID'].nunique()}")
        st.markdown(f"- **Total Sparks Accessed**: {filtered_logs['Spark ID'].nunique()}")

        ### User List
        st.subheader(" User List")
        user_list_df = unique_users[['First Name', 'Last Name', 'User Email']]
        user_list_df['Name'] = user_list_df['First Name'] + ' ' + user_list_df['Last Name']
        st.dataframe(user_list_df[['Name', 'User Email']])

        ### Sparks Accessed
        spark_access = filtered_logs['Spark ID'].value_counts().reset_index()
        spark_access.columns = ['Spark ID', 'Access Count']
        spark_access = spark_access.merge(sparks[['Spark ID', 'Name']], on='Spark ID', how='left')

        st.subheader(" Sparks Accessed")
        st.dataframe(spark_access[['Name', 'Access Count']].rename(columns={'Name': 'Spark Name'}))

        ### % Resources Accessed Per Spark
        st.subheader(" % of Resources Accessed per Spark")
        spark_resource_stats = filtered_logs.groupby('Spark ID').agg({
            'Resources Accessed (%)': 'mean'
        }).reset_index()
        spark_resource_stats = spark_resource_stats.merge(sparks[['Spark ID', 'Name']], on='Spark ID', how='left')
        spark_resource_stats.rename(columns={'Name': 'Spark Name', 'Resources Accessed (%)': 'Avg % Resources Accessed'}, inplace=True)
        st.dataframe(spark_resource_stats[['Spark Name', 'Avg % Resources Accessed']])

        ### Sessions per Spark
        st.subheader("Number of User Sessions per Spark")
        sessions_per_spark = filtered_logs.groupby('Spark ID').agg(
            Total_Sessions=('Access ID', 'nunique'),
            Total_Users=('User ID', 'nunique')
        ).reset_index().merge(
            sparks[['Spark ID', 'Name']],
            on='Spark ID', how='left'
        ).rename(columns={'Name': 'Spark Name'})
        st.dataframe(sessions_per_spark[['Spark Name', 'Total_Sessions', 'Total_Users']])


        ### Line Graph: Accesses over Time
        st.subheader("Accesses Over Time")

        access_over_time = filtered_logs.copy()
        access_over_time['Date'] = access_over_time['Timestamp'].dt.date
        access_counts = access_over_time.groupby('Date').size().reset_index(name='Access Count')

        if not access_counts.empty:
            st.line_chart(access_counts.set_index('Date'))
        else:
            st.info("No access data available for the selected date range.")

        ### Pie Chart: Spark Access Distribution
        st.subheader("Spark Access Distribution")

        if not spark_access.empty:
            # Prepare the data for the pie chart
            spark_access_pie = spark_access.groupby('Name')['Access Count'].sum().reset_index()

            # Create a pie chart using Plotly
            fig_pie = px.pie(
                spark_access_pie,
                names='Name',
                values='Access Count',
                title="Spark Access Distribution",
                color_discrete_sequence=px.colors.qualitative.Set3
            )
            st.plotly_chart(fig_pie)
        else:
            st.info("No Spark access data available for the selected date range.")

        ### Bar Chart: Average Session Length per Spark
        st.subheader("Average Session Length per Spark (minutes)")

        avg_session_length = filtered_logs.groupby('Spark ID').agg(
            Avg_Session_Length=('Session Length (min)', 'mean')
        ).reset_index()

        avg_session_length = avg_session_length.merge(
            sparks[['Spark ID', 'Name']], on='Spark ID', how='left'
        ).rename(columns={'Name': 'Spark Name'})

        if not avg_session_length.empty:
            avg_session_length = avg_session_length.sort_values(by='Avg_Session_Length', ascending=False)

            # Create a bar chart using Plotly Express
            fig = px.bar(
                avg_session_length,
                x='Spark Name',
                y='Avg_Session_Length',
                title="Average Session Length per Spark (minutes)",
                labels={'Avg_Session_Length': 'Average Session Length (minutes)', 'Spark Name': 'Spark Name'},
                color='Spark Name',  # Color bars by the 'Spark Name' to make it colorful
                color_continuous_scale='Viridis'
                # Change this to any other color scale (e.g., 'Blues', 'Cividis', etc.)
            )

            # Update layout (optional: change color theme and other attributes)
            fig.update_layout(
                xaxis_title='Spark',
                yaxis_title='Average Session Length (min)',
                height=600
            )

            # Show the plot
            st.plotly_chart(fig)
        else:
            st.info("No session length data available for the selected date range.")


else:
    st.info("Please upload access_logs.csv, users.csv, and organizations.csv to begin.")

