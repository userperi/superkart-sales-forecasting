# Import necessary libraries
import numpy as np
import pandas as pd
import joblib
from flask import Flask, request, jsonify

# Initialize the Flask application
superkart_api = Flask("SuperKart Sales Predictor")

# Load the trained pipeline (preprocessing + model)
model = joblib.load("superkart_model.joblib")

# Features expected by the model, in the order used for training
FEATURES = [
    "Product_Weight",
    "Product_Sugar_Content",
    "Product_Allocated_Area",
    "Product_MRP",
    "Store_Size",
    "Store_Location_City_Type",
    "Store_Type",
    "Product_Id_char",
    "Store_Age_Years",
    "Product_Type_Category",
]
NUMERIC_FEATURES = ["Product_Weight", "Product_Allocated_Area", "Product_MRP", "Store_Age_Years"]


def prepare_input(df):
    """Validate the columns, keep only the model features and cast numeric types."""
    missing = [col for col in FEATURES if col not in df.columns]
    if missing:
        raise ValueError(f"Missing required feature(s): {missing}")
    df = df[FEATURES].copy()
    for col in NUMERIC_FEATURES:
        df[col] = pd.to_numeric(df[col], errors="raise")
    # Normalise the sugar-content label in the same way as during training
    df["Product_Sugar_Content"] = df["Product_Sugar_Content"].replace("reg", "Regular")
    return df


# Home route (GET) - health check
@superkart_api.get("/")
def home():
    return "Welcome to the SuperKart Sales Prediction API!"


# Online inference: a single product-store record as JSON
@superkart_api.post("/v1/predict")
def predict_sales():
    try:
        data = request.get_json(force=True)
        input_df = prepare_input(pd.DataFrame([data]))
        prediction = model.predict(input_df)[0]
        return jsonify({"Predicted Sales (in dollars)": round(float(prediction), 2)})
    except Exception as e:
        return jsonify({"error": str(e)}), 400


# Batch inference: a CSV file uploaded under the key "file"
@superkart_api.post("/v1/predictbatch")
def predict_sales_batch():
    try:
        if "file" not in request.files:
            return jsonify({"error": "Please upload a CSV file using the key 'file'."}), 400
        file = request.files["file"]
        input_df = prepare_input(pd.read_csv(file))
        predictions = model.predict(input_df)
        # Key = row index of the uploaded file, value = predicted sales
        output = {str(idx): round(float(pred), 2) for idx, pred in zip(input_df.index, predictions)}
        return jsonify(output)
    except Exception as e:
        return jsonify({"error": str(e)}), 400


# Run the app locally (inside Docker it is served by gunicorn)
if __name__ == "__main__":
    superkart_api.run(host="0.0.0.0", port=7860, debug=False)
