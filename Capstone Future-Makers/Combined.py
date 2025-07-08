#  Libraries
import streamlit as st
import pandas as pd
import plotly.express as px
import seaborn as sns
import matplotlib.pyplot as plt
from datetime import datetime

# Function for generating the Account Report in Streamlit
def from_code_account_report(access_logs, users, organizations, sparks):
    # Select an organization from dropdown
    org_options = organizations[['Organization ID', 'Organization Name']].drop_duplicates()
    org_name = st.selectbox("Select an Account (Organization)", org_options['Organization Name'], key="org_select_1")
    org_id = org_options[org_options['Organization Name'] == org_name]['Organization ID'].values[0]

    # Filter users belonging to the selected organization
    org_users = users[users['Organization ID'] == org_id]

    # Display the range of available dates
    min_date = access_logs['Timestamp'].min().date()
    max_date = access_logs['Timestamp'].max().date()
    st.markdown(f"🗓️ **Available Date Range:** {min_date} to {max_date}")

    # Select start and end date within available range
    start_date = st.date_input("Start Date", value=min_date, min_value=min_date, max_value=max_date, key="start_date_input_1")
    end_date = st.date_input("End Date", value=max_date, min_value=min_date, max_value=max_date, key="start_date_input_2")

    # Ensure valid date selection
    if start_date > end_date:
        st.error("Start date must be before end date.")
        return

    # Filter access logs based on organization users and date range
    filtered_logs = access_logs[
        (access_logs['User ID'].isin(org_users['User ID'])) &
        (access_logs['Timestamp'].dt.date >= start_date) &
        (access_logs['Timestamp'].dt.date <= end_date)
    ]

    # --- Organization Summary ---
    st.subheader("Account Info")
    st.markdown(f"**Organization:** {org_name}")
    st.markdown(f"**Total Users:** {org_users.shape[0]}")

    # --- User List Table ---
    st.subheader("User List")
    user_list_df = org_users[['First Name', 'Last Name', 'User Email']].copy()
    user_list_df['Full Name'] = user_list_df['First Name'] + ' ' + user_list_df['Last Name']
    user_table = user_list_df[['Full Name', 'User Email']].sort_values(by='Full Name')
    st.dataframe(user_table.reset_index(drop=True))

    # --- Work Site Table ---
    st.subheader("Site List")
    unique_sites = org_users['Work Address'].dropna().unique()
    if len(unique_sites) > 0:
        site_table = pd.DataFrame(sorted(unique_sites), columns=['Work Address'])
        st.dataframe(site_table.reset_index(drop=True))
    else:
        st.write("No site information available.")

    # --- Define resource interaction columns ---
    resource_cols = [
        'Viewed Slideshow', 'Downloaded Slideshow', 'Watched Tutorial Video',
        'Downloaded AI Playbook', 'Accessed Extension Activities',
        'Used AI Playbook Maker', 'Booked Support Session'
    ]

    # --- List of Sparks accessed by users in the date range ---
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
    spark_resource_usage['Percent Resources Accessed'] = (spark_resource_usage['Resources Accessed'] / len(resource_cols)) * 100
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

    # --- Daily Spark Summary (Sessions & Resources Used) ---
    spark_summary = filtered_logs.groupby([filtered_logs['Timestamp'].dt.date, 'Spark ID'])[resource_cols + ['Access ID']].agg(
        {**{col: 'sum' for col in resource_cols}, 'Access ID': 'nunique'}
    ).reset_index()
    spark_summary['Total Resources Used'] = spark_summary[resource_cols].sum(axis=1)
    spark_summary['Percent Resources Used'] = (spark_summary['Total Resources Used'] / len(resource_cols)).clip(upper=1) * 100
    spark_summary.rename(columns={'Access ID': 'User Sessions'}, inplace=True)
    spark_summary = spark_summary.merge(sparks[['Spark ID', 'Name']], on='Spark ID', how='left')
    spark_summary.rename(columns={'Name': 'Spark Name'}, inplace=True)

    st.subheader("Spark Engagement Summary")
    st.dataframe(spark_summary[['Spark Name', 'User Sessions', 'Percent Resources Used', 'Timestamp']])

    # --- Bar Chart: Percent of Resources Accessed per Spark ---
    resource_usage_per_spark = spark_resource_usage[['Spark Name', 'Percent Resources Accessed']]
    fig1 = px.bar(
        resource_usage_per_spark,
        x='Spark Name',
        y='Percent Resources Accessed',
        title="Percent of Resources Accessed per Spark",
        labels={'Percent Resources Accessed': 'Percentage of Resources Accessed'},
        color='Percent Resources Accessed',
        color_continuous_scale=["gold", "orange", "red"]
    )
    fig1.update_layout(xaxis_title='Spark', yaxis_title='Percentage of Resources Accessed', height=600)
    st.plotly_chart(fig1)

    # --- Box Plot: Session Length per Spark ---
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
    fig2.update_layout(xaxis_title='Spark', yaxis_title='Session Length (min)', height=600)
    fig2.update_traces(line=dict(width=10))  # Optional visual enhancement for trace lines
    st.plotly_chart(fig2)

def from_code_individual_report(access_logs, users, organizations, sparks):
    
    # Create a full name column for user selection
    users['Full Name'] = users['First Name'] + ' ' + users['Last Name']
    selected_user_name = st.selectbox("Select a User", users['Full Name'].unique())

    # Get the selected user's row and extract User ID
    selected_user = users[users['Full Name'] == selected_user_name].iloc[0]
    user_id = selected_user['User ID']
    
    # Define the available date range based on access log timestamps
    min_date = access_logs['Timestamp'].min().date()
    max_date = access_logs['Timestamp'].max().date()
    st.markdown(f"🗓️ **Available Date Range:** {min_date} to {max_date}")
    
    # Date selection inputs for filtering logs
    start_date = st.date_input("Start Date", value=access_logs['Timestamp'].min().date(), key="start_date_input_3")
    end_date = st.date_input("End Date", value=access_logs['Timestamp'].max().date(), key="start_date_input_4")

    # Error if date range is invalid
    if start_date > end_date:
        st.error("Start date must be before end date.")
    else:
        # Filter logs to only include entries for the selected user and date range
        user_logs = access_logs[
            (access_logs['User ID'] == user_id) &
            (access_logs['Timestamp'].dt.date >= start_date) &
            (access_logs['Timestamp'].dt.date <= end_date)
        ]

        # Get organization and site info
        org_id = selected_user['Organization ID']
        organization_name = organizations.loc[organizations['Organization ID'] == org_id, 'Organization Name'].values[0]
        site = selected_user['Work Address']

        # Display user information
        st.subheader("User Info")
        st.markdown(f"**Name:** {selected_user_name}")
        st.markdown(f"**Email:** {selected_user['User Email']}")
        st.markdown(f"**Organization:** {organization_name}")
        st.markdown(f"**Site:** {site if pd.notna(site) else 'N/A'}")

        st.subheader("Session Time per Resource")

        # Define possible activities
        activities = [
            'Viewed Slideshow', 'Downloaded Slideshow', 'Watched Tutorial Video',
            'Accessed Extension Activities', 'Used AI Playbook Maker',
            'Downloaded AI Playbook', 'Booked Support Session'
        ]

        # Reshape log data to long format for activities
        activity_logs = user_logs[['Timestamp'] + activities + ['Session Length (min)']]
        activity_logs = activity_logs.melt(
            id_vars=['Timestamp', 'Session Length (min)'],
            value_vars=activities,
            var_name='Activity',
            value_name='Performed'
        )

        # Keep only performed activities
        activity_logs = activity_logs[activity_logs['Performed'] == 1]

        # Summarize session time by activity
        session_time_per_activity = activity_logs.groupby('Activity')['Session Length (min)'].sum().reset_index()

        # Bar chart: total session time per activity
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

        st.subheader("User Activity Timeline")

        # Reuse the same list of activities
        activities = [
            'Viewed Slideshow', 'Downloaded Slideshow', 'Watched Tutorial Video',
            'Accessed Extension Activities', 'Used AI Playbook Maker',
            'Downloaded AI Playbook', 'Booked Support Session'
        ]

        # Reshape log data again for timeline visualization
        activity_logs = user_logs[['Timestamp'] + activities + ['Session Length (min)']]
        activity_logs = activity_logs.melt(
            id_vars=['Timestamp', 'Session Length (min)'],
            value_vars=activities,
            var_name='Activity',
            value_name='Performed'
        )

        # Keep only entries where activity was performed
        activity_logs = activity_logs[activity_logs['Performed'] == True]

        # Scatter plot: activity over time with session length as bubble size
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

        fig.update_traces(mode='markers+lines') 
        fig.update_layout(
            yaxis_title="Activity",
            xaxis_title="Time",
            legend_title="Activity Type",
            height=600
        )

        st.plotly_chart(fig, use_container_width=True)

        st.subheader("Resource Usage Summary")

        # Summarize total usage of each resource
        resource_cols = [
            'Viewed Slideshow', 'Downloaded Slideshow', 'Watched Tutorial Video',
            'Accessed Extension Activities', 'Used AI Playbook Maker',
            'Downloaded AI Playbook', 'Booked Support Session'
        ]

        resource_totals = user_logs[resource_cols].sum().reset_index()
        resource_totals.columns = ['Resource', 'Count']

        # Keep only resources with at least one usage
        resource_totals = resource_totals[resource_totals['Count'] > 0]

        # Pie chart: distribution of resource usage
        fig2 = px.pie(
            resource_totals,
            values='Count',
            names='Resource',
            title='Resources Used Distribution',
            color_discrete_sequence=px.colors.qualitative.Pastel
        )

        st.plotly_chart(fig2, use_container_width=True)
        
        
def from_code_resource_type_report(access_logs, users, organizations, sparks):
    # Dropdown to select organization
    org_options = organizations[['Organization ID', 'Organization Name']].drop_duplicates()
    org_name = st.selectbox("Select an Account (Organization)", org_options['Organization Name'], key="org_select_2")
    org_id = org_options[org_options['Organization Name'] == org_name]['Organization ID'].values[0]

    # Filter users that belong to the selected organization
    org_users = users[users['Organization ID'] == org_id]
    
    # Determine the available date range for access logs
    min_date = access_logs['Timestamp'].min().date()
    max_date = access_logs['Timestamp'].max().date()
    st.markdown(f"🗓️ **Available Date Range:** {min_date} to {max_date}")

    # Let user pick a date range within the available period
    start_date = st.date_input("Start Date", value=access_logs['Timestamp'].min().date(), key="start_date_input_5")
    end_date = st.date_input("End Date", value=access_logs['Timestamp'].max().date(), key="start_date_input_6")

    # Validate that start date is not after end date
    if start_date > end_date:
        st.error("Start date must be before end date.")
    else:
        # Filter access logs by user IDs and date range
        filtered_logs = access_logs[
            (access_logs['User ID'].isin(org_users['User ID'])) &
            (access_logs['Timestamp'].dt.date >= start_date) &
            (access_logs['Timestamp'].dt.date <= end_date)
        ]

        # Display organization info and total user count
        st.subheader("Account Info")
        st.markdown(f"**Organization:** {org_name}")
        st.markdown(f"**Total Users:** {org_users.shape[0]}")

        # Display list of users in the organization
        st.subheader("User List")
        user_list_df = org_users[['First Name', 'Last Name', 'User Email']].copy()
        user_list_df['Full Name'] = user_list_df['First Name'] + ' ' + user_list_df['Last Name']
        user_list_df = user_list_df[['Full Name', 'User Email']]
        st.dataframe(user_list_df)

        # Display unique site addresses for the organization
        st.subheader("Site List")
        unique_sites = org_users[['Work Address']].dropna().drop_duplicates().reset_index(drop=True)
        unique_sites.index += 1
        unique_sites.columns = ['Site']
        st.dataframe(unique_sites)

        # Define the resource columns to track
        resource_cols = ['Viewed Slideshow', 'Downloaded Slideshow', 'Watched Tutorial Video', 'Downloaded AI Playbook']

        # Count distinct user sessions per Spark
        user_sessions_per_spark = filtered_logs.groupby('Spark ID')['User ID'].nunique().reset_index()
        user_sessions_per_spark.rename(columns={'User ID': 'Sessions'}, inplace=True)
        user_sessions_per_spark = user_sessions_per_spark.merge(sparks[['Spark ID', 'Name']], on='Spark ID', how='left')
        user_sessions_per_spark.rename(columns={'Name': 'Spark Name'}, inplace=True)

        # Show Spark sessions in table format
        st.subheader("User Sessions per Spark")
        st.dataframe(user_sessions_per_spark[['Spark Name', 'Sessions']])

        # Aggregate resource usage and session data per Spark
        spark_summary = filtered_logs.groupby('Spark ID')[resource_cols + ['Access ID']].agg({
            **{col: 'sum' for col in resource_cols},
            'Access ID': 'nunique'
        }).reset_index()

        # Calculate total and percent resource usage
        spark_summary['Total Resources Used'] = spark_summary[resource_cols].sum(axis=1)
        spark_summary['Percent Resources Used'] = (
            spark_summary['Total Resources Used'] / len(resource_cols)
        ).clip(upper=1) * 100
        spark_summary.rename(columns={'Access ID': 'Sessions'}, inplace=True)

        # Join Spark names into the summary
        spark_summary = spark_summary.merge(sparks[['Spark ID', 'Name']], on='Spark ID', how='left')
        spark_summary.rename(columns={'Name': 'Spark Name'}, inplace=True)

        # Display Spark engagement summary
        st.subheader("Spark Engagement Summary")
        st.dataframe(spark_summary[['Spark Name', 'Sessions', 'Percent Resources Used']])

        # Pie chart for total resource usage
        st.subheader("Overall Resource Usage Breakdown")
        total_resource_usage = filtered_logs[resource_cols].sum()

        fig_pie = px.pie(
            names=total_resource_usage.index,
            values=total_resource_usage.values,
            title="Distribution of Resource Interactions",
            color_discrete_sequence=px.colors.qualitative.Set3
        )
        st.plotly_chart(fig_pie)

        # Aggregate and reshape resource usage by Spark
        st.subheader("Resource Usage per Spark")
        resource_usage_data = filtered_logs.groupby('Spark ID')[resource_cols].sum().reset_index()
        resource_usage_data = resource_usage_data.merge(sparks[['Spark ID', 'Name']], on='Spark ID', how='left')
        resource_usage_data.set_index('Name', inplace=True)
        resource_usage_data = resource_usage_data[resource_cols]
        resource_usage_reset = resource_usage_data.reset_index()

        # Melt data for plotting
        melted_data = resource_usage_reset.melt(id_vars='Name', var_name='Resource Type', value_name='Interactions')

        # Bubble chart to visualize resource interaction intensity per Spark
        st.markdown("### Bubble Chart: Resource Interactions per Spark")
        fig_bubble, ax_bubble = plt.subplots(figsize=(12, 6))
        sns.scatterplot(
            data=melted_data,
            x='Name',
            y='Resource Type',
            size='Interactions',
            hue='Interactions',
            sizes=(20, 300), 
            palette='coolwarm',
            legend=False,
            alpha=0.7
        )
        plt.xticks(rotation=45, ha='right')
        plt.title('Resource Interactions per Spark (Bubble Chart)')
        plt.xlabel('Spark Name')
        plt.ylabel('Resource Type')
        st.pyplot(fig_bubble)


def from_code_site_report(access_logs, users, organizations, sparks):

    # Dropdown to select an organization
    org_options = organizations[['Organization ID', 'Organization Name']].drop_duplicates()
    org_name = st.selectbox("Select an Account (Organization)", org_options['Organization Name'], key="org_select_3")
    org_id = org_options[org_options['Organization Name'] == org_name]['Organization ID'].values[0]

    # Filter users from the selected organization
    org_users = users[users['Organization ID'] == org_id]

    # Define available date range based on access logs
    min_date = access_logs['Timestamp'].min().date()
    max_date = access_logs['Timestamp'].max().date()
    st.markdown(f"🗓️ **Available Date Range:** {min_date} to {max_date}")

    # User selects the date range to analyze
    start_date = st.date_input("Start Date", value=min_date, min_value=min_date, max_value=max_date, key="start_date_input_7")
    end_date = st.date_input("End Date", value=max_date, min_value=min_date, max_value=max_date, key="end_date_input_8")

    # Check for valid date range
    if start_date > end_date:
        st.error("Start date must be before end date.")
        return

    # Filter logs for users in organization and within date range
    filtered_logs = access_logs[
        (access_logs['User ID'].isin(org_users['User ID'])) &
        (access_logs['Timestamp'].dt.date >= start_date) &
        (access_logs['Timestamp'].dt.date <= end_date)
    ]

    # Get users who were active during the filtered period
    unique_users = org_users[org_users['User ID'].isin(filtered_logs['User ID'])]

    # Display summary stats
    st.subheader("Site Summary")
    st.markdown(f"- **Total Users (active in range)**: {unique_users['User ID'].nunique()}")
    st.markdown(f"- **Total Sparks Accessed**: {filtered_logs['Spark ID'].nunique()}")

    # Show list of users with names and emails
    st.subheader("User List")
    user_list_df = unique_users[['First Name', 'Last Name', 'User Email']].copy()
    user_list_df['Name'] = user_list_df['First Name'] + ' ' + user_list_df['Last Name']
    st.dataframe(user_list_df[['Name', 'User Email']])

    # Count how many times each Spark was accessed
    spark_access = filtered_logs['Spark ID'].value_counts().reset_index()
    spark_access.columns = ['Spark ID', 'Access Count']
    spark_access = spark_access.merge(sparks[['Spark ID', 'Name']], on='Spark ID', how='left')

    # Show spark access counts
    st.subheader("Sparks Accessed")
    st.dataframe(spark_access[['Name', 'Access Count']].rename(columns={'Name': 'Spark Name'}))

    # Show average percent of resources accessed per Spark
    st.subheader("% of Resources Accessed per Spark")
    spark_resource_stats = filtered_logs.groupby('Spark ID').agg({
        'Resources Accessed (%)': 'mean'
    }).reset_index()
    spark_resource_stats = spark_resource_stats.merge(sparks[['Spark ID', 'Name']], on='Spark ID', how='left')
    spark_resource_stats.rename(columns={'Name': 'Spark Name', 'Resources Accessed (%)': 'Avg % Resources Accessed'}, inplace=True)
    st.dataframe(spark_resource_stats[['Spark Name', 'Avg % Resources Accessed']])

    # Count total sessions and distinct users per Spark
    st.subheader("Number of User Sessions per Spark")
    sessions_per_spark = filtered_logs.groupby('Spark ID').agg(
        Total_Sessions=('Access ID', 'nunique'),
        Total_Users=('User ID', 'nunique')
    ).reset_index().merge(
        sparks[['Spark ID', 'Name']],
        on='Spark ID', how='left'
    ).rename(columns={'Name': 'Spark Name'})
    st.dataframe(sessions_per_spark[['Spark Name', 'Total_Sessions', 'Total_Users']])

    # Prepare data to visualize access over time
    st.subheader("Accesses Over Time")
    access_over_time = filtered_logs.copy()
    access_over_time['Date'] = access_over_time['Timestamp'].dt.date
    access_counts = access_over_time.groupby('Date').size().reset_index(name='Access Count')

    # Line chart showing access trends by day
    if not access_counts.empty:
        st.line_chart(access_counts.set_index('Date'))
    else:
        st.info("No access data available for the selected date range.")

    # Pie chart for distribution of Spark access
    st.subheader("Spark Access Distribution")
    if not spark_access.empty:
        spark_access_pie = spark_access.groupby('Name')['Access Count'].sum().reset_index()

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

    # Bar chart of average session lengths per Spark
    st.subheader("Average Session Length per Spark (minutes)")
    avg_session_length = filtered_logs.groupby('Spark ID').agg(
        Avg_Session_Length=('Session Length (min)', 'mean')
    ).reset_index()

    avg_session_length = avg_session_length.merge(
        sparks[['Spark ID', 'Name']], on='Spark ID', how='left'
    ).rename(columns={'Name': 'Spark Name'})

    if not avg_session_length.empty:
        avg_session_length = avg_session_length.sort_values(by='Avg_Session_Length', ascending=False)

        fig = px.bar(
            avg_session_length,
            x='Spark Name',
            y='Avg_Session_Length',
            title="Average Session Length per Spark (minutes)",
            labels={'Avg_Session_Length': 'Average Session Length (minutes)', 'Spark Name': 'Spark Name'},
            color='Spark Name', 
            color_continuous_scale='Viridis'
        )

        fig.update_layout(
            xaxis_title='Spark',
            yaxis_title='Average Session Length (min)',
            height=600
        )

        st.plotly_chart(fig)
    else:
        st.info("No session length data available for the selected date range.")

def from_code_sparks_report(access_logs, users, organizations, sparks):

    # Select organization to filter users and logs
    selected_org = st.selectbox("Select Organization", organizations['Organization Name'].unique())

    # Select date range for report
    start_date = st.date_input("Start Date", value=access_logs['Timestamp'].min().date(), key="start_date_input_9")
    end_date = st.date_input("End Date", value=access_logs['Timestamp'].max().date(), key="start_date_input_10")

    # Error if start date is after end date
    if start_date > end_date:
        st.error("Start date must be before end date.")
    else:
        # Filter users belonging to the selected organization
        org_users = users[users['Organization ID'].isin(
            organizations[organizations['Organization Name'] == selected_org]['Organization ID']
        )]

        # Filter access logs by selected users and date range
        filtered_logs = access_logs[
            (access_logs['User ID'].isin(org_users['User ID'])) &
            (access_logs['Timestamp'].dt.date >= start_date) &
            (access_logs['Timestamp'].dt.date <= end_date)
        ]

        # Count unique sessions per Spark
        sessions_per_spark = filtered_logs.groupby('Spark ID')['Access ID'].nunique().reset_index()
        sessions_per_spark = sessions_per_spark.merge(sparks, left_on='Spark ID', right_on='Spark ID', how='left')
        sessions_per_spark.rename(columns={'Access ID': 'Sessions', 'Name': 'Spark Name'}, inplace=True)

        st.subheader("Sessions per Spark")
        st.dataframe(sessions_per_spark[['Spark Name', 'Sessions']])

        # Aggregate resource usage and calculate percent used
        resource_cols = ['Viewed Slideshow', 'Downloaded Slideshow', 'Watched Tutorial Video', 'Downloaded AI Playbook']
        spark_resource_usage = filtered_logs.groupby('Spark ID')[resource_cols].sum().reset_index()
        spark_resource_usage['Total'] = spark_resource_usage[resource_cols].sum(axis=1)
        spark_resource_usage['Percent Used'] = (
            spark_resource_usage['Total'] /
            (len(resource_cols) * filtered_logs.groupby('Spark ID').size())
        ).fillna(0) * 100
        spark_resource_usage = spark_resource_usage.merge(sparks, left_on='Spark ID', right_on='Spark ID', how='left')

        st.subheader("Percentage of Resources Accessed per Spark")
        st.dataframe(spark_resource_usage[['Name', 'Percent Used']].rename(columns={'Name': 'Spark Name'}))

        # Show associated organization ID and sites
        associated_org_id = organizations[organizations['Organization Name'] == selected_org]['Organization ID'].values[0]
        associated_sites = org_users['Work Address'].dropna().unique()

        st.subheader("Accounts and Sites Associated")
        st.markdown(f"**Organization:** {selected_org} (ID: {associated_org_id})")
        st.markdown(f"**Sites:** {', '.join(associated_sites.astype(str)) if len(associated_sites) > 0 else 'None'}")

        # Show list of users and emails
        st.subheader("Users Associated")
        user_list = org_users[['First Name', 'Last Name', 'User Email']].copy()
        user_list['Name'] = user_list['First Name'] + ' ' + user_list['Last Name']
        st.dataframe(user_list[['Name', 'User Email']].rename(columns={'User Email': 'Email'}))

        # Show top Sparks by session count and engagement
        st.subheader("Top Sparks by Sessions and Engagement")
        top_sparks = sessions_per_spark.sort_values(by='Sessions', ascending=False).head(10)
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

        # Show overall access totals for each resource type
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
                xaxis_tickangle=0,
                height=500,
                showlegend=False,
            )

            st.plotly_chart(fig2)
        else:
            st.info("No resource access data available to display.")

        # Show sessions over time as a line chart
        st.subheader("Sessions Over Time")
        sessions_over_time = filtered_logs.copy()
        sessions_over_time['Date'] = sessions_over_time['Timestamp'].dt.date
        sessions_by_date = sessions_over_time.groupby('Date').size().reset_index(name='Sessions')

        if not sessions_by_date.empty:
            st.line_chart(sessions_by_date.set_index('Date')['Sessions'])
        else:
            st.info("No session activity data for the selected period.")

# --- Streamlit App Setup ---

# Set page configuration
st.set_page_config(page_title="Spark Engagement Reports", layout="wide")

# Sidebar inputs for CSV uploads
st.sidebar.header("Upload CSV Files")
access_logs_file = st.sidebar.file_uploader("Upload access_logs.csv", type=["csv"])
users_file = st.sidebar.file_uploader("Upload users.csv", type=["csv"])
organizations_file = st.sidebar.file_uploader("Upload organizations.csv", type=["csv"])
sparks_file = st.sidebar.file_uploader("Upload sparks.csv", type=["csv"])

# Create tabs for different report types
tabs = st.tabs([
    "Account Report",
    "Individual User Report",
    "Resource Type Report",
    "Site Engagement Report",
    "Sparks Report"
])

# Run reports if all files are uploaded
if access_logs_file and users_file and organizations_file and sparks_file:
    access_logs = pd.read_csv(access_logs_file)
    users = pd.read_csv(users_file)
    organizations = pd.read_csv(organizations_file)
    sparks = pd.read_csv(sparks_file)

    # Convert timestamp column to datetime
    access_logs['Timestamp'] = pd.to_datetime(access_logs['Timestamp'])

    with tabs[0]:
        st.title("Account-Level Spark Engagement Report")
        from_code_account_report(access_logs, users, organizations, sparks)

    with tabs[1]:
        st.title("Individual User Spark Engagement Report")
        from_code_individual_report(access_logs, users, organizations, sparks)

    with tabs[2]:
        st.title("Resource Type Usage Report")
        from_code_resource_type_report(access_logs, users, organizations, sparks)

    with tabs[3]:
        st.title("Site Engagement Report Generator")
        from_code_site_report(access_logs, users, organizations, sparks)
        
    with tabs[4]:
        st.title("Sparks Report Generator")
        from_code_sparks_report(access_logs, users, organizations, sparks)
else:
    st.warning("Please upload all required files (access_logs, users, organizations, sparks) to see reports.")
    
