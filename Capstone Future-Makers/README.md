# FutureMakers Engagement Dashboard – Capstone Project

**Authors:** Maria Andreina Sisco, Hannah Hodges, Quentin McIntosh-Giles, and Jose Ojea

**Project:** DS496 Ethical Data Science Capstone  
**Institution:** Loyola University Maryland  
**Date Completed:** May 2025

---

## Project Overview

This capstone project, completed in collaboration with **FutureMakers**, delivers a scalable dashboard system to track and analyze educator engagement with their *Sparks kits*.

FutureMakers is a mission-driven education organization that empowers educators and students by providing creative, hands-on, and future-ready learning resources (*Sparks*). The client, Matt Barinholtz (Founder & CEO), partnered with our team to design a prototype reporting tool that would eventually support real-time data analysis across partner schools and organizations.

The core deliverable is a dynamic, interactive Streamlit dashboard that allows FutureMakers to upload and analyze usage data through five modular reports. In the absence of live data, a fully relational mock database was constructed based on actual platform features and client requirements.

---

## Key Features

- **Five Interactive Reports**:
    - Account Report
    - Individual User Report
    - Site Report
    - Resource Type Report
    - Sparks Report
- **Real-Time CSV Upload**: Supports dynamic input of access logs, user info, organizations, and Spark kits.
- **Advanced Visualizations**: Includes timelines, bar charts, pie charts, and session summaries powered by Plotly and Seaborn.
- **Modular Codebase**: Each report is defined as a function in `Combined.py` and can be maintained or expanded independently.
- **Streamlit Web App**: Runs locally and generates a clean, tab-based user interface for non-technical users.

---

## File Structure

```
📁 FutureMakers-Dashboard/
├── Combined.py             # Main Streamlit app with all report logic
├── AccountReport.py        # (Optional) Separated reports by type
├── Individual.py
├── SiteReport.py
├── ResourceType.py
├── SparksReport.py
├── access_logs.csv         # Mock access log data
├── users.csv               # Mock user data
├── organizations.csv       # Mock org data
├── sparks.csv              # Static file – do not modify
```

---

## How to Run

1. Ensure Python 3.x is installed.
2. Install required packages:

```bash
pip install streamlit pandas plotly seaborn matplotlib
```

3. Navigate to the project directory in terminal:

```bash
cd path/to/FutureMakers-Dashboard
```

4. Run the Streamlit app:

```bash
streamlit run Combined.py
```

5. The dashboard will open in your default browser as a **localhost** webpage. Upload the required `.csv` files through the sidebar to begin exploring reports.

---

## Important Notes

- Do **not** rename or modify column headers in the CSV files. The system depends on exact field names.
- `sparks.csv` is static and should remain unchanged.
- You can replace the mock data with real user data once available.

