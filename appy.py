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

    # Smooth data using 10-second averaging
    if 'T(sec)' in df.columns:
        df['T(sec)'] = pd.to_numeric(df['T(sec)'], errors='coerce')
        df = df.sort_values('T(sec)')
        df = df.set_index('T(sec)')
        numeric_df = df.select_dtypes(include=['number'])
        smoothed_df = numeric_df.rolling(window=10, min_periods=1).mean()
        df.update(smoothed_df)
        df = df.reset_index()
    df.columns = df.columns.str.strip()
    for col in df.columns:
        df[col] = pd.to_numeric(df[col], errors='ignore')

    st.subheader("🧾 Test Information")
    st.markdown(f"**Name:** {first_name} {last_name}  ")
    st.markdown(f"**Date of Test:** {test_date}  ")
    st.markdown(f"**Gender:** {gender}  ")
    st.markdown(f"**Age:** {age}  ")
    st.markdown(f"**Height:** {height} cm  ")
    st.markdown(f"**Weight:** {weight} kg  ")
    st.markdown(f"**Target Weight:** {target_weight} kg  ")

    def rank_vo2_max(vo2, age, gender):
        vo2_tables = {
            'Male': {
                (13, 19): [34.9, 38.3, 45.1, 50.9, 55.9],
                (20, 29): [32.9, 36.4, 42.4, 46.4, 52.4],
                (30, 39): [31.4, 35.4, 40.9, 44.9, 49.4],
                (40, 49): [30.1, 33.5, 38.9, 43.7, 48.0],
                (50, 59): [25.9, 30.9, 35.7, 39.9, 45.3],
                (60, 69): [20.3, 26.0, 32.2, 36.4, 44.2]
            },
            'Female': {
                (13, 19): [24.9, 30.9, 34.9, 38.9, 41.9],
                (20, 29): [23.5, 28.9, 32.9, 36.9, 41.0],
                (30, 39): [22.7, 26.9, 31.4, 35.6, 40.0],
                (40, 49): [20.9, 24.4, 28.9, 32.8, 36.9],
                (50, 59): [20.1, 22.7, 26.9, 31.4, 35.7],
                (60, 69): [17.4, 20.1, 24.4, 30.2, 31.4]
            }
        }
        for (min_age, max_age), thresholds in vo2_tables[gender].items():
            if min_age <= age <= max_age:
                if vo2 <= thresholds[0]: return "Very Poor"
                elif vo2 <= thresholds[1]: return "Poor"
                elif vo2 <= thresholds[2]: return "Fair"
                elif vo2 <= thresholds[3]: return "Good"
                elif vo2 <= thresholds[4]: return "Excellent"
                else: return "Superior"
        return "Unknown"

    st.subheader("🏃‍♂️ Core VO₂ Max Test Metrics")
    if 'VO2(ml/min)' in df.columns:
        peak_vo2 = df['VO2(ml/min)'].max()
        vo2_kg = peak_vo2 / weight
        st.markdown("**VO₂ (ml/min) – Oxygen Consumption**\n\nMeasures how much oxygen your body is using at any given intensity. Peak VO₂ is a top indicator of aerobic fitness.")
        st.metric("VO₂ Max (ml/min)", f"{peak_vo2:.0f}")
        st.markdown("**VO₂ per kg (ml/kg/min) – Relative Oxygen Consumption**\n\nAdjusts VO₂ for body weight. Useful for comparing fitness across individuals.")
        ranking = rank_vo2_max(vo2_kg, age, gender)
        st.metric("VO₂ Max (ml/kg/min)", f"{vo2_kg:.2f}", delta=ranking)

        st.markdown("**Male VO₂ Max Ratings (ml/kg/min)**")
        male_table = pd.DataFrame({
            "Age Range": ["13-19", "20-29", "30-39", "40-49", "50-59", "60-69"],
            "Very Poor": ["0–34.9", "0–32.9", "0–31.4", "0–30.1", "0–25.9", "0–20.3"],
            "Poor": ["35–38.3", "33–36.4", "31.5–35.4", "30.2–33.5", "26–30.9", "20.4–26.0"],
            "Fair": ["38.4–45.1", "36.5–42.4", "35.5–40.9", "33.6–38.9", "31–35.7", "26.1–32.2"],
            "Good": ["45.2–50.9", "42.5–46.4", "41–44.9", "39–43.7", "35.8–39.9", "32.3–36.4"],
            "Excellent": ["51–55.9", "46.5–52.4", "45–49.4", "43.8–48.0", "41–45.3", "36.5–44.2"],
            "Superior": ["56+", "52.5+", "49.5+", "48.1+", "45.4+", "44.3+"]
        })
        st.dataframe(male_table, hide_index=True)

        st.markdown("**Female VO₂ Max Ratings (ml/kg/min)**")
        female_table = pd.DataFrame({
            "Age Range": ["13-19", "20-29", "30-39", "40-49", "50-59", "60-69"],
            "Very Poor": ["0–24.9", "0–23.5", "0–22.7", "0–20.9", "0–20.1", "0–17.4"],
            "Poor": ["25–30.9", "23.6–28.9", "22.8–26.9", "21–24.4", "20.2–22.7", "17.5–20.1"],
            "Fair": ["31–34.9", "29–32.9", "27–31.4", "24.5–28.9", "22.8–26.9", "20.2–24.4"],
            "Good": ["35–38.9", "33–36.9", "31.5–35.6", "29–32.8", "27–31.4", "24.5–30.2"],
            "Excellent": ["39–41.9", "37–41", "35.7–40", "32.9–36.9", "31.5–35.7", "30.3–31.4"],
            "Superior": ["42+", "41.1+", "40.1+", "37+", "35.8+", "31.5+"]
        })
        st.dataframe(female_table, hide_index=True)

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
        fatmax_hr = int(round(df.loc[fatmax_idx, 'HR(bpm)'])) if 'HR(bpm)' in df.columns else 'N/A'
        st.markdown(f"**FatMax Zone**\n\nFat oxidation peaked at HR: **{fatmax_hr} bpm**")

        first_crossover = df[(df['CARBS(%)'] > df['FAT(%)']) & (df['T(sec)'] > 100)].head(1)
        if not first_crossover.empty and 'HR(bpm)' in first_crossover.columns:
            crossover_hr = int(round(first_crossover['HR(bpm)'].values[0]))
            st.markdown(f"**Crossover Point**  \
Carbs surpassed fat as the dominant fuel at HR: **{crossover_hr} bpm**")
        else:
            st.markdown("**Crossover Point**  \
No clear crossover detected after 100 seconds.")

    st.subheader("🫁 Breathing Efficiency Metrics")
    if 'BF(bpm)' in df.columns:
        st.markdown("""**Breathing Frequency (BF, bpm)**  
Breaths per minute; a rise with low ventilation could indicate shallow or inefficient breathing.""")
        st.metric("Peak Breathing Frequency", f"{df['BF(bpm)'].max():.0f} bpm")

    if 'VT(l)' in df.columns:
        st.markdown("""**Tidal Volume (VT, L)**  
Volume of air per breath. Deep, efficient breathing results in a higher VT at lower BF.""")
        st.metric("Peak Tidal Volume", f"{df['VT(l)'].max():.2f} L")

    

    st.subheader("🧘 Recovery Metrics")
    if 'HR(bpm)' in df.columns:
        recovery_1min = df['HR(bpm)'].iloc[-1] - df['HR(bpm)'].iloc[-6]
        recovery_2min = df['HR(bpm)'].iloc[-1] - df['HR(bpm)'].iloc[-12]
        st.metric("Heart Rate Recovery (1 min)", f"{int(round(recovery_1min))} bpm")
        st.metric("Heart Rate Recovery (2 min)", f"{int(round(recovery_2min))} bpm")

        half_recovery_time_sec = (df['T(sec)'].iloc[-1] - df['T(sec)'].iloc[-6])

        if half_recovery_time_sec < 60:
            recovery_interpretation = "🚀 Elite metabolic recovery"
        elif 60 <= half_recovery_time_sec <= 120:
            recovery_interpretation = "✅ Good recovery"
        elif 120 < half_recovery_time_sec <= 180:
            recovery_interpretation = "⚠️ Delayed recovery"
        else:
            recovery_interpretation = "❌ Impaired recovery (clinical concern)"

        st.markdown(f"**Heart Rate Half-Recovery Time:** {half_recovery_time_sec:.0f} seconds")
        st.markdown(f"**Recovery Interpretation:** {recovery_interpretation}")

    if 'VCO2(ml/min)' in df.columns:
        recovery_vco2_1min = df['VCO2(ml/min)'].iloc[-1] - df['VCO2(ml/min)'].iloc[-6]
        recovery_vco2_2min = df['VCO2(ml/min)'].iloc[-1] - df['VCO2(ml/min)'].iloc[-12]
        st.metric("VCO₂ Recovery (1 min)", f"{recovery_vco2_1min:.2f} ml/min")
        st.metric("VCO₂ Recovery (2 min)", f"{recovery_vco2_2min:.2f} ml/min")

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
        vt1_hr = int(round(df.loc[vt1_idx, 'HR(bpm)'])) if 'HR(bpm)' in df.columns else 'N/A'
        vt2_candidates = df[df['HR(bpm)'] > vt1_hr]
        vt2_idx = vt2_candidates['VE/VCO2'].idxmax() if not vt2_candidates.empty else None
        vt2_hr = int(round(df.loc[vt2_idx, 'HR(bpm)'])) if vt2_idx is not None and 'HR(bpm)' in df.columns else 'N/A'
 
        st.markdown(f"**Ventilatory Threshold 1 (VT1)**  \nEstimated at HR: **{int(vt1_hr)} bpm** — indicates the transition to moderate intensity.")
        st.markdown(f"**Ventilatory Threshold 2 (VT2)**  \nEstimated at HR: **{int(vt2_hr)} bpm** — marks onset of intense anaerobic effort.")

    
    
