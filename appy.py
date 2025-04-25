import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np

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
    for col in df.columns:
        df[col] = pd.to_numeric(df[col], errors='ignore')

    st.subheader("📋 Raw Data")
    st.dataframe(df.head())

    def rank_vo2_max(vo2, age, gender):
        thresholds = {
            'Male': [(13, 30), (33, 40), (37, 45), (41, 50), (45, 60)],
            'Female': [(11, 28), (30, 35), (33, 40), (37, 45), (41, 50)]
        }
        for rank, (low, high) in zip(["Very Poor", "Poor", "Fair", "Good", "Excellent"], thresholds[gender]):
            if low <= vo2 <= high:
                return rank
        return "Superior" if vo2 > thresholds[gender][-1][1] else "Very Poor"

    st.subheader("🏃‍♂️ Core VO₂ Max Test Metrics")
    if 'VO2(ml/min)' in df.columns:
        peak_vo2 = df['VO2(ml/min)'].max()
        vo2_kg = peak_vo2 / weight
        st.markdown("**VO₂ (ml/min) – Oxygen Consumption**\n\nMeasures how much oxygen your body is using at any given intensity. Peak VO₂ is a top indicator of aerobic fitness.")
        st.metric("VO₂ Max (ml/min)", f"{peak_vo2:.0f}")
        st.markdown("**VO₂ per kg (ml/kg/min) – Relative Oxygen Consumption**\n\nAdjusts VO₂ for body weight. Useful for comparing fitness across individuals.")
        ranking = rank_vo2_max(vo2_kg, age, gender)
        st.metric("VO₂ Max (ml/kg/min)", f"{vo2_kg:.2f}", delta=ranking)

    if 'HR(bpm)' in df.columns:
        st.markdown("**Heart Rate (HR, bpm) – Cardiac Effort**\n\nShows cardiovascular response. Important for training zones and recovery.")
        st.metric("Max Heart Rate", f"{df['HR(bpm)'].max():.0f} bpm")

    if 'RER' in df.columns:
        st.markdown("**Respiratory Exchange Ratio (RER)**\n\nIndicates fuel usage: ~0.7=fat, ~1.0=carb. >1.1 often means VO₂ max effort.")
        st.metric("Max RER", f"{df['RER'].max():.2f}")

    if 'VCO2(ml/min)' in df.columns:
        st.markdown("**VCO₂ (ml/min) – Carbon Dioxide Output**\n\nUsed with VO₂ to detect anaerobic threshold.")
        st.metric("Max VCO₂", f"{df['VCO2(ml/min)'].max():.0f}")

    if 'VE(l/min)' in df.columns:
        st.markdown("**Ventilation (VE, L/min) – Air Volume per Minute**\n\nReflects respiratory demand and efficiency.")
        st.metric("Max VE", f"{df['VE(l/min)'].max():.1f} L/min")

    if 'MET' in df.columns:
        st.markdown("**METs (Metabolic Equivalents)**\n\nMeasures effort relative to resting metabolism.")
        st.metric("Peak METs", f"{df['MET'].max():.1f}")

    st.subheader("🔥 Energy Metabolism Metrics")
    if 'EE(kcal/min)' in df.columns:
        st.markdown("**Energy Expenditure (kcal/min)**\n\nCalories burned per minute. Useful for energy needs and diet planning.")
        st.metric("Peak EE", f"{df['EE(kcal/min)'].max():.1f} kcal/min")

    if 'FAT(%)' in df.columns and 'CARBS(%)' in df.columns:
        st.markdown("**Fat vs. Carbohydrate Utilization**\n\nRepresents relative fuel sources.")
        avg_carbs = df['CARBS(%)'].mean()
        avg_fat = df['FAT(%)'].mean()
        fig, ax = plt.subplots()
        ax.pie([avg_carbs, avg_fat], labels=['Carbs', 'Fat'], autopct='%1.1f%%', startangle=90)
        st.pyplot(fig)

        fatmax_idx = df['FAT(%)'].idxmax()
        fatmax_hr = df.loc[fatmax_idx, 'HR(bpm)'] if 'HR(bpm)' in df.columns else 'N/A'
        st.markdown(f"**FatMax Zone**\n\nFat oxidation peaked at HR: **{fatmax_hr} bpm**")

        crossover_idx = df[df['CARBS(%)'] > df['FAT(%)']].first_valid_index()
        crossover_hr = df.loc[crossover_idx, 'HR(bpm)'] if crossover_idx and 'HR(bpm)' in df.columns else 'N/A'
        st.markdown(f"**Crossover Point**\n\nCarbs surpassed fat as primary fuel at HR: **{crossover_hr} bpm**")

    st.subheader("🧘 Recovery Metrics")
    if 'HR(bpm)' in df.columns:
        recovery_hr = df['HR(bpm)'].iloc[-1] - df['HR(bpm)'].iloc[-10]
        st.metric("Heart Rate Recovery", f"{recovery_hr:.2f} bpm")

    if 'VCO2(ml/min)' in df.columns:
        recovery_vco2 = df['VCO2(ml/min)'].iloc[-1] - df['VCO2(ml/min)'].iloc[-10]
        st.metric("VCO₂ Recovery", f"{recovery_vco2:.2f} ml/min")

    if 'RER' in df.columns:
        st.markdown("**RER Recovery Trend**")
        fig, ax = plt.subplots()
        sns.lineplot(data=df, x=df.index, y='RER', ax=ax)
        st.pyplot(fig)

    st.subheader("📊 Metric Trends")
    numeric_cols = df.select_dtypes(include=['float64', 'int64']).columns
    selected_col = st.selectbox("Select Metric to Plot", numeric_cols)
    fig, ax = plt.subplots()
    sns.lineplot(data=df, x=df.index, y=selected_col, ax=ax)
    st.pyplot(fig)

    st.subheader("📊 Performance Threshold Metrics")
    if 'VE(l/min)' in df.columns and 'VCO2(ml/min)' in df.columns:
        df['VE/VCO2'] = df['VE(l/min)'] / df['VCO2(ml/min)']
        vt1_idx = df['VE/VCO2'].idxmin()
        vt1_hr = df.loc[vt1_idx, 'HR(bpm)'] if 'HR(bpm)' in df.columns else 'N/A'
        vt2_idx = df['VE/VCO2'].idxmax()
        vt2_hr = df.loc[vt2_idx, 'HR(bpm)'] if 'HR(bpm)' in df.columns else 'N/A'

        st.markdown(f"**Ventilatory Threshold 1 (VT1)**
Estimated at HR: **{vt1_hr} bpm** — indicates the transition to moderate intensity.")
        st.markdown(f"**Ventilatory Threshold 2 (VT2)**
Estimated at HR: **{vt2_hr} bpm** — marks onset of intense anaerobic effort.")

    st.subheader("📉 Summary Statistics")
    st.write(df[numeric_cols].describe())
