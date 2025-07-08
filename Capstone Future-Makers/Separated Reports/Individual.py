import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import datetime

st.set_page_config(page_title="Individual User Report", layout="wide")
st.title("Individual User Spark Engagement Report")

# Upload section
st.sidebar.header("Upload CSV Files")
access_logs_file = st.sidebar.file_uploader("Upload access_logs.csv", type=["csv"])
users_file = st.sidebar.file_uploader("Upload users.csv", type=["csv"])
organizations_file = st.sidebar.file_uploader("Upload organizations.csv", type=["csv"])

# Load static sparks file
sparks = pd.read_csv("sparks.csv")  # Make sure this file exists in your directory

if access_logs_file and users_file and organizations_file:
    access_logs = pd.read_csv(access_logs_file)
    users = pd.read_csv(users_file)
    organizations = pd.read_csv(organizations_file)
    access_logs['Timestamp'] = pd.to_datetime(access_logs['Timestamp'])

    # Select a user
    users['Full Name'] = users['First Name'] + ' ' + users['Last Name']
    selected_user_name = st.selectbox("Select a User", users['Full Name'].unique())

    selected_user = users[users['Full Name'] == selected_user_name].iloc[0]
    user_id = selected_user['User ID']

    start_date = st.date_input("Start Date", value=access_logs['Timestamp'].min().date())
    end_date = st.date_input("End Date", value=access_logs['Timestamp'].max().date())

    if start_date > end_date:
        st.error("Start date must be before end date.")
    else:
        user_logs = access_logs[
            (access_logs['User ID'] == user_id) &
            (access_logs['Timestamp'].dt.date >= start_date) &
            (access_logs['Timestamp'].dt.date <= end_date)
        ]

        # Display basic info
        org_id = selected_user['Organization ID']
        organization_name = organizations.loc[organizations['Organization ID'] == org_id, 'Organization Name'].values[0]
        site = selected_user['Work Address']

        st.subheader("User Info")
        st.markdown(f"**Name:** {selected_user_name}")
        st.markdown(f"**Email:** {selected_user['User Email']}")
        st.markdown(f"**Organization:** {organization_name}")
        st.markdown(f"**Site:** {site if pd.notna(site) else 'N/A'}")

        # -------------- Graph 1: Session Time per Resource --------------
        st.subheader("Session Time per Resource")

        activities = [
            'Viewed Slideshow', 'Downloaded Slideshow', 'Watched Tutorial Video',
            'Accessed Extension Activities', 'Used AI Playbook Maker',
            'Downloaded AI Playbook', 'Booked Support Session'
        ]

        # Melt to long format
        activity_logs = user_logs[['Timestamp'] + activities + ['Session Length (min)']]
        activity_logs = activity_logs.melt(
            id_vars=['Timestamp', 'Session Length (min)'],
            value_vars=activities,
            var_name='Activity',
            value_name='Performed'
        )

        # Filter only performed activities
        activity_logs = activity_logs[activity_logs['Performed'] == 1]

        # Group by Activity and sum session times
        session_time_per_activity = activity_logs.groupby('Activity')['Session Length (min)'].sum().reset_index()

        # Create Bar Chart
        fig = px.bar(
            session_time_per_activity,
            x='Activity',
            y='Session Length (min)',
            title='Total Session Time per Resource',
            labels={'Session Length (min)': 'Total Session Time (minutes)'},
            color='Session Length (min)',
            color_continuous_scale=["lightskyblue", "darkblue"]
        )

        fig.update_layout(
            xaxis_title='Resource',
            yaxis_title='Total Session Time (min)',
            height=600
        )

        st.plotly_chart(fig, use_container_width=True)

        # -------------- Graph 2: User Activity Timeline --------------
        st.subheader("User Activity Timeline")

        # Activities to plot
        activities = [
            'Viewed Slideshow', 'Downloaded Slideshow', 'Watched Tutorial Video',
            'Accessed Extension Activities', 'Used AI Playbook Maker',
            'Downloaded AI Playbook', 'Booked Support Session'
        ]

        # Prepare the data for plotting
        activity_logs = user_logs[['Timestamp'] + activities + ['Session Length (min)']]

        # Melt to long format
        activity_logs = activity_logs.melt(
            id_vars=['Timestamp', 'Session Length (min)'],
            value_vars=activities,
            var_name='Activity',
            value_name='Performed'
        )

        # Keep only rows where the activity was performed (True)
        activity_logs = activity_logs[activity_logs['Performed'] == True]

        # Plot
        fig = px.scatter(
            activity_logs,
            x="Timestamp",
            y="Activity",
            size="Session Length (min)",
            color="Activity",
            hover_data=["Session Length (min)"],
            title=f"Journey of {selected_user_name}",
            labels={"Session Length (min)": "Session Length (min)"},
        )

        fig.update_traces(mode='markers+lines')  # Connect activities by lines
        fig.update_layout(
            yaxis_title="Activity",
            xaxis_title="Time",
            legend_title="Activity Type",
            height=600
        )

        st.plotly_chart(fig, use_container_width=True)

        # -------------- Graph 2.5: User Activity Timeline --------------

        activity_logs['End'] = activity_logs['Timestamp'] + pd.to_timedelta(activity_logs['Session Length (min)'],
                                                                            unit='m')

        # Plot using a timeline
        fig = px.timeline(
            activity_logs,
            x_start="Timestamp",
            x_end="End",
            y="Activity",
            color="Activity",
            title=f"Journey of {selected_user_name}",
            labels={"Activity": "Activity Type"},
            hover_data=["Session Length (min)"]
        )

        fig.update_yaxes(autorange="reversed")  # Activities in chronological order top-down
        fig.update_layout(
            height=600,
            xaxis_title="Time",
            yaxis_title="Activity"
        )

        st.plotly_chart(fig, use_container_width=True)
        # -------------- Graph 3: Resource Usage Summary --------------
        st.subheader("Resource Usage Summary")

        resource_cols = [
            'Viewed Slideshow', 'Downloaded Slideshow', 'Watched Tutorial Video',
            'Accessed Extension Activities', 'Used AI Playbook Maker',
            'Downloaded AI Playbook', 'Booked Support Session'
        ]

        resource_totals = user_logs[resource_cols].sum().reset_index()
        resource_totals.columns = ['Resource', 'Count']

        # Remove resources with 0 count
        resource_totals = resource_totals[resource_totals['Count'] > 0]

        fig2 = px.pie(
            resource_totals,
            values='Count',
            names='Resource',
            title='Resources Used Distribution',
            color_discrete_sequence=px.colors.qualitative.Pastel
        )

        st.plotly_chart(fig2, use_container_width=True)

else:
    st.info("Please upload access_logs, users, and organizations CSV files to begin.")
