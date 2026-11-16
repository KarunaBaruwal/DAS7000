
import streamlit as st
import pandas as pd
import plotly.express as px

# Page settings
st.set_page_config(
    page_title="Chicago Crime Patterns",
    layout="wide"
)

# Simple page styling
st.markdown("""
<style>
    .stApp {
        background-color: #F8FAFC;
        color: #1E293B;
    }

    h1, h2, h3 {
        color: #183153;
    }

    div[data-testid="stMetric"] {
        background-color: white;
        border: 1px solid #E2E8F0;
        border-radius: 10px;
        padding: 15px;
    }
</style>
""", unsafe_allow_html=True)


# Load dataset
df = pd.read_csv("Chicago_Crime.csv")

# Check data before cleaning
missing_before = df.isnull().sum()
duplicates = df["ID"].duplicated().sum()
original_columns = len(df.columns)

# Clean the dataset
df["Location Description"] = df["Location Description"].fillna("Unknown")

df["Date"] = pd.to_datetime(
    df["Date"],
    format="%m/%d/%Y %I:%M:%S %p",
    errors="coerce"
)

df["Community Area"] = df["Community Area"].astype("Int64")
df["Month"] = df["Date"].dt.month


# Main heading
st.title("Chicago Crime Patterns (2021–2025)")
st.caption("Exploring crime types, police districts and arrest patterns")

# Create two tabs
tab1, tab2 = st.tabs(["Charts & Analysis", "Data Information"])


# TAB 1 - CHARTS AND ANALYSIS
with tab1:

    st.subheader("Explore Crime Data")

    # Filters
    col1, col2 = st.columns(2)

    with col1:
        years = sorted(df["Year"].dropna().unique())

        selected_years = st.multiselect(
            "Select Year",
            years,
            default=years
        )

    with col2:
        crime_types = sorted(df["Primary Type"].dropna().unique())

        selected_crimes = st.multiselect(
            "Select Crime Type",
            crime_types,
            default=crime_types
        )

    # Filter the data
    filtered_df = df[
        df["Year"].isin(selected_years) &
        df["Primary Type"].isin(selected_crimes)
    ]

    # Summary cards
    st.subheader("Crime Snapshot")

    total = len(filtered_df)
    categories = filtered_df["Primary Type"].nunique()

    if total > 0:
        arrest_rate = filtered_df["Arrest"].mean() * 100
    else:
        arrest_rate = 0

    col1, col2, col3 = st.columns(3)

    col1.metric("Sample Records", f"{total:,}")
    col2.metric("Crime Categories", categories)
    col3.metric("Arrest Rate", f"{arrest_rate:.1f}%")

    st.divider()

    if total == 0:
        st.warning("No records match the selected filters.")

    else:
        # Chart 1 and Chart 2
        left, right = st.columns(2)

        with left:
            st.subheader("Most Frequently Reported Crime Types")

            crime_count = (
                filtered_df["Primary Type"]
                .value_counts()
                .head(10)
            )

            fig1 = px.bar(
                x=crime_count.values,
                y=crime_count.index,
                orientation="h",
                labels={
                    "x": "Sample Records",
                    "y": "Crime Type"
                },
                color_discrete_sequence=["#0D9488"]
            )

            fig1.update_layout(
                yaxis={"categoryorder": "total ascending"},
                height=380
            )

            st.plotly_chart(fig1, use_container_width=True)

        with right:
            st.subheader("Records by Police District")

            district_count = (
                filtered_df["District"]
                .value_counts()
                .sort_index()
            )

            fig2 = px.bar(
                x=district_count.index.astype(str),
                y=district_count.values,
                labels={
                    "x": "Police District",
                    "y": "Sample Records"
                },
                color_discrete_sequence=["#3B82F6"]
            )

            fig2.update_layout(
                height=380,
                xaxis_type="category"
            )

            st.plotly_chart(fig2, use_container_width=True)

        # Chart 3 - Monthly patterns
        st.subheader("Monthly Crime Patterns")

        monthly_count = (
            filtered_df["Month"]
            .value_counts()
            .sort_index()
        )

        fig3 = px.line(
            x=monthly_count.index,
            y=monthly_count.values,
            markers=True,
            labels={
                "x": "Month",
                "y": "Sample Records"
            }
        )

        fig3.update_traces(line_color="#0D9488")

        fig3.update_layout(
            height=320,
            xaxis=dict(
                tickmode="array",
                tickvals=list(range(1, 13)),
                ticktext=[
                    "Jan", "Feb", "Mar", "Apr",
                    "May", "Jun", "Jul", "Aug",
                    "Sep", "Oct", "Nov", "Dec"
                ]
            )
        )

        st.plotly_chart(fig3, use_container_width=True)

        # Chart 4 - Arrest rates
        st.subheader("Arrest Rate by Crime Type")

        # Count records in each crime category
        crime_sizes = filtered_df["Primary Type"].value_counts()

        # Keep categories with at least 20 sampled records
        valid_crimes = crime_sizes[crime_sizes >= 20].index

        arrest_data = filtered_df[
            filtered_df["Primary Type"].isin(valid_crimes)
        ]

        arrest_data = (
            arrest_data.groupby("Primary Type")["Arrest"]
            .mean() * 100
        )

        arrest_data = arrest_data.sort_values(
            ascending=False
        ).head(10)

        if arrest_data.empty:
            st.info("Not enough records to compare arrest rates.")
        else:
            fig4 = px.bar(
                x=arrest_data.values,
                y=arrest_data.index,
                orientation="h",
                labels={
                    "x": "Arrest Rate (%)",
                    "y": "Crime Type"
                },
                color_discrete_sequence=["#D97706"]
            )

            fig4.update_layout(
                yaxis={"categoryorder": "total ascending"},
                xaxis_range=[0, 100],
                height=400
            )

            st.plotly_chart(fig4, use_container_width=True)

        st.caption(
            "The arrest-rate chart only includes crime types "
            "with at least 20 records in the selected sample."
        )

        # Findings
        st.subheader("Key Findings")

        most_common = (
            filtered_df["Primary Type"]
            .value_counts()
            .idxmax()
        )

        busiest_district = (
            filtered_df["District"]
            .value_counts()
            .idxmax()
        )

        st.write("Most frequent crime type:", most_common)
        st.write("District with most sampled records:", busiest_district)
        st.write("Overall arrest rate:", f"{arrest_rate:.1f}%")

    st.caption(
        "This analysis uses a sample of Chicago crime records. "
        "The figures do not represent total crimes across the city."
    )


# TAB 2 - DATA INFORMATION
with tab2:

    st.header("Dataset Information")

    col1, col2, col3 = st.columns(3)

    col1.metric("Total Records", f"{len(df):,}")
    col2.metric("Original Columns", original_columns)
    col3.metric("Duplicate IDs", duplicates)

    st.subheader("Dataset Preview")
    st.dataframe(df.head(10), use_container_width=True)

    #st.subheader("Missing Values Before Cleaning")
    #st.write(missing_before)

    #st.subheader("Data Types")
    #st.write(df.dtypes)

    st.subheader("Cleaning Summary")

    st.write("Records after cleaning:", len(df))
    st.write("Missing values after cleaning:", df.isnull().sum().sum())
    st.write("Duplicate IDs:", duplicates)

    st.info(
        "Missing location descriptions were replaced with 'Unknown'. "
        "Dates were converted into datetime format, and a Month "
        "column was created for analysis."
    )
