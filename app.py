import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px

st.set_page_config(page_title="📦 RM Safety Stock App", layout="wide")

st.title("📦 Raw Material Safety Stock & Forecasting Tool")

st.markdown("""
Upload the following 3 Excel files:
1. **RM Master** – Contains RM Code, RM Name, Min/Max Order Qty
2. **RM Consumption Data (2024-2025)** – Monthly plant-wise RM usage
3. **FG Production Data (2024-2025)** – Monthly plant-wise FG production to estimate demand seasonality
""")

rm_file = st.file_uploader("⬆️ Upload RM Master File", type=["xlsx"])
rm_consumption_file = st.file_uploader("⬆️ Upload RM Consumption File", type=["xlsx"])
fg_production_file = st.file_uploader("⬆️ Upload FG Production File", type=["xlsx"])

# Check if all files are uploaded
if rm_file and rm_consumption_file and fg_production_file:
    try:
        # Read master
        rm_master = pd.read_excel(rm_file)

        # Read RM and FG files with multi-level columns
        rm_df = pd.read_excel(rm_consumption_file, header=[0, 1])
        fg_df = pd.read_excel(fg_production_file, header=[0, 1])

        st.success("All files uploaded and read successfully! 🟢")

        st.write("### 📋 RM Master Data")
        st.dataframe(rm_master.head())

        # Map months to custom seasons
        season_map = {
            'January': 'Winter', 'February': 'Winter', 'March': 'Summer',
            'April': 'Summer', 'May': 'Summer', 'June': 'Monsoon',
            'July': 'Monsoon', 'August': 'Monsoon', 'September': 'Monsoon',
            'October': 'Monsoon', 'November': 'Winter', 'December': 'Winter'
        }

        st.header("📊 Seasonal Analysis & Safety Stock")

        # Simplify RM consumption file – assuming 'RM Code' is the identifier in first column
        if 'RM Code' in rm_df.columns:
            rm_df = rm_df.set_index('RM Code')

        # Flatten multiindex to process easier
        rm_df.columns = [f"{month}_{plant}" for month, plant in rm_df.columns]

        seasonal_data = []
        lead_time_days = 8

        for idx, row in rm_df.iterrows():
            rm_code = idx
            monthly_totals = {}

            for col in row.index:
                month = col.split("_")[0]
                val = row[col]
                if pd.notna(val):
                    if month in monthly_totals:
                        monthly_totals[month] += val
                    else:
                        monthly_totals[month] = val

            # Group by season
            season_summary = {}
            for month, value in monthly_totals.items():
                season = season_map.get(month, 'Unknown')
                season_summary.setdefault(season, []).append(value)

            for season, values in season_summary.items():
                avg = np.mean(values)
                maxv = np.max(values)
                safety_stock = (avg / 30) * lead_time_days
                reorder_level = (maxv / 30) * lead_time_days
                seasonal_data.append({
                    'RM Code': rm_code,
                    'Season': season,
                    'Avg Monthly Usage': round(avg,2),
                    'Max Usage': round(maxv,2),
                    'Safety Stock': round(safety_stock,2),
                    'Reorder Level': round(reorder_level,2),
                })

        result_df = pd.DataFrame(seasonal_data)

        # Merge with RM Names
        if 'RM Code' in rm_master.columns:
            result_df = result_df.merge(rm_master[['RM Code', 'RM Name']], on='RM Code', how='left')

        # Show table
        st.dataframe(result_df)

        # Plot Example
        st.write("### 📈 Sample Seasonality Plot")
        selected_rm = st.selectbox("Choose RM Code to Visualize", result_df['RM Code'].unique())
        rm_plot_df = result_df[result_df['RM Code'] == selected_rm]

        fig = px.bar(rm_plot_df, x='Season', y='Avg Monthly Usage',
                     title=f"Seasonal Demand for {selected_rm}", color='Season')
        st.plotly_chart(fig)

        # Download
        to_download = result_df.to_csv(index=False).encode('utf-8')
        st.download_button("📥 Download Safety Stock Data", to_download, file_name="rm_safety_stock.csv", mime='text/csv')

    except Exception as e:
        st.error(f"⚠️ Error processing the files: {e}")

else:
    st.info("Please upload all three required Excel files to proceed.")
