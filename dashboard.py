import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt

# Cleaned file path
cleaned_file_path = "cleaned_data.xlsx"

# Load the cleaned data
@st.cache_data
def load_data():
    return pd.read_excel(cleaned_file_path, engine="openpyxl")  # Explicitly set the engine

data = load_data()


# Sidebar navigation to select pages
page = st.sidebar.selectbox("Select a Page:", [
    "Ready for Review Applications",
    "Support by Demographics",
    "Processing Time Analysis",
    "Grant Utilization Analysis",
    "Stakeholder Summary"
])

# Page 1: Ready for Review Applications
if page == "Ready for Review Applications":
    st.title("Applications Ready for Review")

    # Filter applications that are "Ready for Review" (i.e., "Request Status" == "Pending")
    ready_for_review = data[data["Request Status"] == "Pending"]

    st.subheader("Applications Ready for Review")
    st.dataframe(ready_for_review)

    # Dropdown to filter by "Application Signed?"
    signed_status = st.selectbox("Filter by Application Signed Status", ["All", "Yes", "No", "Missing"])

    if signed_status != "All":
        filtered_data = ready_for_review[ready_for_review["Application Signed?"] == signed_status]
    else:
        filtered_data = ready_for_review

    st.subheader("Filtered Applications")
    st.dataframe(filtered_data)


    # Add bar chart for count of "Yes" and "No" in "Application Signed?"
    st.subheader("Count of Signed vs. Unsigned Applications")

    # Count occurrences of "Yes" and "No"
    signed_counts = ready_for_review["Application Signed?"].value_counts()

    # Keep only "Yes" and "No"
    signed_counts = signed_counts.loc[signed_counts.index.isin(["Yes", "No"])]

    # Create bar chart
    fig, ax = plt.subplots()
    ax.bar(signed_counts.index, signed_counts.values, color=["blue", "red"])
    ax.set_xlabel("Application Signed?")
    ax.set_ylabel("Count")
    ax.set_title("Signed vs. Unsigned Applications")

    st.pyplot(fig)


# Page 2: Support by Demographics
elif page == "Support by Demographics":
    st.title("Support Given by Demographics")

    # Select demographic filters
    demographic = st.selectbox("Select Demographic Category:", [
        "Pt City", "Pt State", "Pt Zip", "Language", "Marital Status", "Gender",
        "Race", "Hispanic/Latino", "Sexual Orientation", "Household Size",
        "Monthly Household Income Range", "Insurance Type", "Age"
    ])

    # Group and summarize support based on selected category
    support_summary = data.groupby(demographic)["Amount"].sum().reset_index()

    st.subheader(f"Total Support Given by {demographic}")
    st.dataframe(support_summary)


# Page 3: Processing Time Analysis
if page == "Processing Time Analysis":
    st.title("Processing Time Analysis")

    # Drop rows where either Grant Req Date or Payment Date is missing
    data = data.dropna(subset=["Grant Req Date", "Payment Submitted?"])

    # Display summary statistics
    st.subheader("Key Metrics")
    st.write(f"Average Processing Time: {data['Processing Time (Days)'].mean():.2f} days")
    st.write(f"Median Processing Time: {data['Processing Time (Days)'].median():.2f} days")
    st.write(f"Minimum Processing Time: {data['Processing Time (Days)'].min()} days")
    st.write(f"Maximum Processing Time: {data['Processing Time (Days)'].max()} days")

    # Display processing time distribution using Matplotlib
    st.subheader("Processing Time Distribution")

    fig, ax = plt.subplots()
    ax.hist(data["Processing Time (Days)"], bins=20, edgecolor="black")
    ax.set_xlabel("Processing Time (Days)")
    ax.set_ylabel("Number of Requests")
    ax.set_title("Distribution of Processing Time")

    st.pyplot(fig)  # Display the plot in Streamlit

    # Show data table for review
    st.subheader("Processing Time Per Request")
    st.dataframe(data[["Grant Req Date", "Payment Submitted?", "Processing Time (Days)"]])


# Page 4: Grant Utilization Analysis
if page == "Grant Utilization Analysis":
    st.title("Grant Utilization Analysis")

    # Filter patients who did not use their full grant
    unused_grants = data[data["Remaining Balance"] > 0]

    # Display total count of patients who left money unused, broken out by App Year
    st.subheader("Patients Who Did Not Use Full Grant (By Application Year)")
    unused_by_year = unused_grants.groupby("App Year")["Patient ID#"].count().reset_index()
    unused_by_year.columns = ["Application Year", "Total Patients"]
    st.dataframe(unused_by_year)

    # Calculate average given amount (instead of remaining balance), grouped by Assistance Type
    st.subheader("Average Amount Given by Assistance Type")
    avg_given_by_assistance = data.groupby("Type of Assistance (CLASS)")["Amount"].mean().reset_index()
    st.dataframe(avg_given_by_assistance)

    # Optional: Visualization
    st.subheader("Average Grant Given by Assistance Type")
    st.bar_chart(avg_given_by_assistance.set_index("Type of Assistance (CLASS)"))


# Page 5: Stakeholder Impact Summary
if page == "Stakeholder Summary":
    st.title("Foundation Impact & Progress Summary")

    # Total patients assisted
    total_patients = data["Patient ID#"].nunique()
    st.subheader("Total Patients Assisted")
    st.write(f"{total_patients} patients received grants.")

    # Total amount granted
    total_granted = data["Amount"].sum()
    st.subheader("Total Amount Granted")
    st.write(f"${total_granted:,.2f} provided in assistance.")

    # Average grant per patient
    avg_grant_per_patient = total_granted / total_patients
    st.subheader("Average Grant Per Patient")
    st.write(f"${avg_grant_per_patient:,.2f} per patient on average.")

    # Processing Efficiency
    avg_processing_time = data["Processing Time (Days)"].mean()
    st.subheader("Processing Efficiency")
    st.write(f"Average processing time: {avg_processing_time:.2f} days.")

    # Breakdown of assistance types
    st.subheader("Funds Allocated by Assistance Type")
    assistance_summary = data.groupby("Type of Assistance (CLASS)")["Amount"].sum().reset_index()
    st.dataframe(assistance_summary)

    # Utilization Rate
    fully_used = data[data["Remaining Balance"] == 0].shape[0]
    utilization_rate = (fully_used / total_patients) * 100
    st.subheader("Grant Utilization Rate")
    st.write(f"{utilization_rate:.2f}% of patients fully used their grant.")

    # Demographics Summary
    st.subheader("Patient Demographics")
    demographic_summary = data[["Pt City", "Pt State", "Pt Zip", "Language", "Marital Status", "Gender", "Race", "Hispanic/Latino", "Sexual Orientation", "Household Size","Monthly Household Income Range", "Insurance Type", "Age"]].value_counts().reset_index()
    st.dataframe(demographic_summary)

    # Optional: Visualization
    st.subheader("Grant Distribution by Assistance Type")
    st.bar_chart(assistance_summary.set_index("Type of Assistance (CLASS)"))