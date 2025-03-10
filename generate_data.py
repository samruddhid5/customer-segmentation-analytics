import pandas as pd
import random
import json
from faker import Faker

fake = Faker()

def generate_customer_data(min_transactions=5000):
    """Generate synthetic customer data ensuring at least min_transactions rows in the CSV."""
    customers = []
    total_transactions = 0
    
    while total_transactions < min_transactions:
        customer_id = fake.uuid4()
        name = fake.name()
        email = fake.email()
        join_date = fake.date_between(start_date='-2y', end_date='today')
        
        # Additional customer features
        age = random.randint(18, 80)
        gender = random.choice(['Male', 'Female', 'Other'])
        city = fake.city()
        country = fake.country()
        loyalty_status = random.choice(['Bronze', 'Silver', 'Gold', 'Platinum'])
        signup_source = random.choice(['Website', 'Mobile App', 'In-Store'])
        customer_type = random.choice(['New', 'Returning', 'VIP'])
        
        # Generate a random number of transactions for the customer (between 1 and 10)
        num_transactions = random.randint(1, 10)
        transactions = []
        for _ in range(num_transactions):
            transaction = {
                "transaction_id": fake.uuid4(),
                "date": fake.date_between(start_date=join_date, end_date='today').isoformat(),
                "amount": round(random.uniform(10, 500), 2),
                "product": fake.word(),
                "product_category": random.choice(['Electronics', 'Fashion', 'Home', 'Sports', 'Books']),
                "quantity": random.randint(1, 5),
                "discount": round(random.uniform(0, 0.3), 2),  # discount as a fraction
                "payment_method": random.choice(['Credit Card', 'PayPal', 'Debit Card', 'Cash']),
                "purchase_channel": random.choice(['Online', 'In-Store'])
            }
            transactions.append(transaction)
        
        total_transactions += num_transactions
        
        customer_record = {
            "customer_id": customer_id,
            "name": name,
            "email": email,
            "join_date": join_date.isoformat(),
            "age": age,
            "gender": gender,
            "city": city,
            "country": country,
            "loyalty_status": loyalty_status,
            "signup_source": signup_source,
            "customer_type": customer_type,
            "transactions": transactions
        }
        customers.append(customer_record)
    
    return customers

def save_data(customers):
    # Flatten the data for CSV export
    transaction_list = []
    for customer in customers:
        for trans in customer["transactions"]:
            transaction_list.append({
                "customer_id": customer["customer_id"],
                "name": customer["name"],
                "email": customer["email"],
                "join_date": customer["join_date"],
                "age": customer["age"],
                "gender": customer["gender"],
                "city": customer["city"],
                "country": customer["country"],
                "loyalty_status": customer["loyalty_status"],
                "signup_source": customer["signup_source"],
                "customer_type": customer["customer_type"],
                "transaction_id": trans["transaction_id"],
                "transaction_date": trans["date"],
                "transaction_amount": trans["amount"],
                "product": trans["product"],
                "product_category": trans["product_category"],
                "quantity": trans["quantity"],
                "discount": trans["discount"],
                "payment_method": trans["payment_method"],
                "purchase_channel": trans["purchase_channel"]
            })
    df = pd.DataFrame(transaction_list)
    df.to_csv('synthetic_transactions.csv', index=False)
    print(f"CSV file generated: synthetic_transactions.csv with {df.shape[0]} rows")
    
    # Write the nested customer data to a JSON file
    with open('synthetic_customers.json', 'w') as f:
        json.dump(customers, f, indent=4)
    print("JSON file generated: synthetic_customers.json")

if __name__ == '__main__':
    customer_data = generate_customer_data(min_transactions=5000)
    save_data(customer_data)
