from flask import Flask, jsonify
import json
import pandas as pd
from sklearn.preprocessing import StandardScaler
from sklearn.cluster import KMeans

app = Flask(__name__)

# Load synthetic customer data from the JSON file
with open('synthetic_customers.json', 'r') as f:
    customer_data = json.load(f)

@app.route('/api/customers', methods=['GET'])
def get_customers():
    # Returns the synthetic customer data as JSON
    return jsonify(customer_data)

@app.route('/api/segments', methods=['GET'])
def get_segments():
    # Load the CSV data containing transaction details
    df = pd.read_csv('synthetic_transactions.csv')
    
    # Select features for clustering (adjust or add features as needed)
    features = df[['transaction_amount', 'quantity']]
    
    # Scale the features
    scaler = StandardScaler()
    features_scaled = scaler.fit_transform(features)
    
    # Apply KMeans clustering
    kmeans = KMeans(n_clusters=4, random_state=42)
    df['cluster'] = kmeans.fit_predict(features_scaled)
    
    # Aggregate segmentation info: one record per customer (e.g., first transaction per customer)
    segments = df.groupby('customer_id').first().reset_index()[['customer_id', 'cluster']]
    return jsonify(segments.to_dict(orient='records'))

@app.route('/api/transactions', methods=['GET'])
def get_transactions():
    import pandas as pd
    # Load the synthetic transactions data from CSV
    df_transactions = pd.read_csv('synthetic_transactions.csv')
    # Optionally, convert any date columns to strings if needed:
    if 'transaction_date' in df_transactions.columns:
        df_transactions['transaction_date'] = pd.to_datetime(df_transactions['transaction_date']).astype(str)
    return jsonify(df_transactions.to_dict(orient='records'))


if __name__ == '__main__':
    app.run(debug=True)
