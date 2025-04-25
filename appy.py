import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import io

st.set_page_config(page_title="VO2 Max Test Analyzer", layout="wide")
st.title("VO2 Max Test Analyzer")

# Sidebar for user inputs
st.sidebar.header("User Information")
first_name = st.sidebar.text_input("First Name")
last_name = st.sidebar.text_input("Last Name")
test_date = st.sidebar.date_input("Date of Test")
gender = st.sidebar.selectbox("Gender", ["Male", "Female"]) 
age = st.sidebar.number_input("Age", min_value=10, max_value=100, step=1)
height = st.sidebar.number_input("Height (cm)", min_value=100, max_value=250, step=1)
weight = st.sidebar.number_input("Weight (kg)", min_value=30.0, max_value=200.0, step=0.1)
target_weight = st.sidebar.number_input("Target Weight (kg)", min_value=30.0, max_value=200.0, step=0.1)

# File upload
st.header("Upload VO2 Max CSV Data")
uploaded_file = st.file_uploader("Choose a CSV file", type="csv")

if uploaded_file:
    df = pd.read_csv(uploaded_file, sep=';', engine='python')
    df.columns = df.columns.str.strip()

    st.subheader("Raw Data")
    st.dataframe(df.head())

    # Convert columns to numeric where possible
    for col in df.columns:
        df[col] = pd.to_numeric(df[col], errors='ignore')

    # VO2 Max and age-based ranking (basic ACSM categories)
    def rank_vo2_max(vo2, age, gender):
        thresholds = {
            'Male': [(13, 30), (33, 40), (37, 45), (41, 50), (45, 60)],
            'Female': [(11, 28), (30, 35), (33, 40), (37, 45), (41, 50)]
        }
        for rank, (low, high) in zip(["Very Poor", "Poor", "Fair", "Good", "Excellent"], thresholds[gender]):
            if low <= vo2 <= high:
                return rank
        return "Superior" if vo2 > thresholds[gender][-1][1] else "Very Poor"

    if 'VO2(ml/min)' in df.columns:
        peak_vo2 = df['VO2(ml/min)'].max()
        vo2_kg = peak_vo2 / weight
        ranking = rank_vo2_max(vo2_kg, age, gender)
        st.metric(label="Estimated VO2 Max (ml/kg/min)", value=f"{vo2_kg:.2f}", delta=ranking)

    # Plotting section
    st.subheader("Graphs & Analysis")

    numeric_cols = df.select_dtypes(include=['float64', 'int64']).columns
    selected_col = st.selectbox("Select Metric to Plot", numeric_cols)

    fig, ax = plt.subplots()
    sns.lineplot(data=df, x=df.index, y=selected_col, ax=ax)
    ax.set_title(f"{selected_col} Over Time")
    ax.set_xlabel("Sample Point")
    ax.set_ylabel(selected_col)
    st.pyplot(fig)

    if 'CARBS(%)' in df.columns and 'FAT(%)' in df.columns:
        avg_carbs = df['CARBS(%)'].mean()
        avg_fat = df['FAT(%)'].mean()

        fig2, ax2 = plt.subplots()
        ax2.pie([avg_carbs, avg_fat], labels=['Carbs', 'Fat'], autopct='%1.1f%%', startangle=90)
        ax2.set_title("Average Substrate Utilization")
        st.pyplot(fig2)

    # Recovery metrics
    st.subheader("Recovery Metrics")
    if 'HR(bpm)' in df.columns:
        recovery_hr = df['HR(bpm)'].iloc[-1] - df['HR(bpm)'].iloc[-10]
        st.metric(label="Heart Rate Recovery (last vs -10 point)", value=f"{recovery_hr:.2f} bpm")

    if 'VCO2(ml/min)' in df.columns:
        recovery_vco2 = df['VCO2(ml/min)'].iloc[-1] - df['VCO2(ml/min)'].iloc[-10]
        st.metric(label="VCO2 Recovery (last vs -10 point)", value=f"{recovery_vco2:.2f} ml/min")

    # RER trends
    if 'RER' in df.columns:
        st.subheader("RER Over Time")
        fig3, ax3 = plt.subplots()
        sns.lineplot(data=df, x=df.index, y='RER', ax=ax3)
        ax3.set_title("RER Trend")
        ax3.set_xlabel("Sample Point")
        ax3.set_ylabel("RER")
        st.pyplot(fig3)

    # Summary statistics
    st.subheader("Summary Statistics")
    st.write(df[numeric_cols].describe())
