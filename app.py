import streamlit as st

st.title("📦 Raw Material Safety Stock App")
st.write("Upload Excel files to get analysis")

rm_file = st.file_uploader("Upload RM Master Excel", type=["xlsx"])
rm_consumption_file = st.file_uploader("Upload RM Consumption Excel", type=["xlsx"])
fg_production_file = st.file_uploader("Upload FG Production Excel", type=["xlsx"])

if rm_file and rm_consumption_file and fg_production_file:
    st.success("Files uploaded.")
else:
    st.info("Waiting for you to upload all files.")