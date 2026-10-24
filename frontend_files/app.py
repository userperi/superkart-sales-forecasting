import os
import requests
import pandas as pd
import streamlit as st

# Backend URL: inside the Docker network the backend container is reachable by its name
BACKEND_URL = os.getenv("BACKEND_URL", "http://superkart-backend:7860")

PERISHABLES = ["Dairy", "Meat", "Fruits and Vegetables", "Breakfast", "Breads", "Seafood"]
PRODUCT_TYPES = sorted(PERISHABLES + [
    "Snack Foods", "Frozen Foods", "Household", "Baking Goods", "Canned", "Health and Hygiene",
    "Soft Drinks", "Hard Drinks", "Starchy Foods", "Others",
])
REFERENCE_YEAR = 2025

st.set_page_config(page_title="SuperKart Sales Forecast", page_icon="🛒", layout="centered")
st.title("🛒 SuperKart Sales Forecasting")
st.write("Predict the total sales revenue of a product in a store for the upcoming quarter.")

tab_online, tab_batch = st.tabs(["Single prediction", "Batch prediction"])

# ------------------------- Online prediction -------------------------
with tab_online:
    st.subheader("Product details")
    col1, col2 = st.columns(2)
    with col1:
        product_id_char = st.selectbox("Product family (Product ID prefix)", ["FD", "NC", "DR"],
                                       help="FD = Food, NC = Non-Consumable, DR = Drinks")
        product_type = st.selectbox("Product type", PRODUCT_TYPES)
        sugar_content = st.selectbox("Sugar content", ["Low Sugar", "Regular", "No Sugar"])
    with col2:
        product_weight = st.number_input("Product weight", min_value=0.0, max_value=50.0, value=12.66, step=0.01)
        product_mrp = st.number_input("Product MRP", min_value=0.0, max_value=1000.0, value=147.0, step=0.01)
        allocated_area = st.number_input("Allocated display area (ratio)", min_value=0.0, max_value=1.0,
                                         value=0.056, step=0.001, format="%.3f")

    st.subheader("Store details")
    col3, col4 = st.columns(2)
    with col3:
        store_type = st.selectbox("Store type", ["Supermarket Type1", "Supermarket Type2",
                                                 "Departmental Store", "Food Mart"])
        store_size = st.selectbox("Store size", ["High", "Medium", "Small"])
    with col4:
        city_type = st.selectbox("City tier", ["Tier 1", "Tier 2", "Tier 3"])
        est_year = st.number_input("Store establishment year", min_value=1950, max_value=REFERENCE_YEAR,
                                   value=2009, step=1)

    payload = {
        "Product_Weight": product_weight,
        "Product_Sugar_Content": sugar_content,
        "Product_Allocated_Area": allocated_area,
        "Product_MRP": product_mrp,
        "Store_Size": store_size,
        "Store_Location_City_Type": city_type,
        "Store_Type": store_type,
        "Product_Id_char": product_id_char,
        "Store_Age_Years": int(REFERENCE_YEAR - est_year),
        "Product_Type_Category": "Perishables" if product_type in PERISHABLES else "Non Perishables",
    }

    if st.button("Predict sales", type="primary"):
        try:
            response = requests.post(f"{BACKEND_URL}/v1/predict", json=payload, timeout=30)
            if response.status_code == 200:
                prediction = response.json()["Predicted Sales (in dollars)"]
                st.success(f"Predicted product-store sales: **${prediction:,.2f}**")
            else:
                st.error(f"Prediction failed ({response.status_code}): {response.text}")
        except requests.exceptions.RequestException as e:
            st.error(f"Could not reach the prediction service: {e}")

# ------------------------- Batch prediction -------------------------
with tab_batch:
    st.write("Upload a CSV file with the columns: Product_Weight, Product_Sugar_Content, "
             "Product_Allocated_Area, Product_MRP, Store_Size, Store_Location_City_Type, Store_Type, "
             "Product_Id_char, Store_Age_Years, Product_Type_Category.")
    uploaded_file = st.file_uploader("Upload CSV file", type=["csv"])

    if uploaded_file is not None:
        batch_df = pd.read_csv(uploaded_file)
        st.dataframe(batch_df.head())
        if st.button("Predict batch"):
            try:
                response = requests.post(
                    f"{BACKEND_URL}/v1/predictbatch",
                    files={"file": ("batch.csv", batch_df.to_csv(index=False).encode("utf-8"), "text/csv")},
                    timeout=60,
                )
                if response.status_code == 200:
                    preds = response.json()
                    batch_df["Predicted_Sales"] = [preds[str(i)] for i in range(len(batch_df))]
                    st.success(f"Predicted sales for {len(batch_df)} records "
                               f"(total ${batch_df['Predicted_Sales'].sum():,.2f}).")
                    st.dataframe(batch_df)
                    st.download_button("Download predictions", batch_df.to_csv(index=False).encode("utf-8"),
                                       file_name="superkart_predictions.csv", mime="text/csv")
                else:
                    st.error(f"Batch prediction failed ({response.status_code}): {response.text}")
            except requests.exceptions.RequestException as e:
                st.error(f"Could not reach the prediction service: {e}")
