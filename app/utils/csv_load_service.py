import pandas as pd
from pydantic import ValidationError
from app.db.mongodb import MongoDB
from app.models.payment import Payment
from app.core.logging import Logger
from datetime import datetime


async def load_and_normalize_csv_data(file_path: str, collection_name: str):
    logger = Logger.get_logger(__name__)
    logger.info(f"Loading data from '{file_path}'")

    # Check if the collection is empty
    count = await MongoDB.db[collection_name].count_documents({})
    if count > 0:
        logger.info(f"Data already exists in the collection '{collection_name}'. Skipping CSV load.")
        return
    
    # Read CSV data
    df = pd.read_csv(file_path)
    
    # Normalize data (example: ensure all fields conform to the schema)
    df = df.apply(lambda x: x.str.strip() if x.dtype == "object" else x)
    
    # # Convert date columns to UTC timestamps and then to string
    df["payee_due_date"] = pd.to_datetime(df["payee_due_date"], utc=True).dt.strftime('%Y-%m-%dT%H:%M:%SZ')
    
    # Convert the `payee_due_date` column to datetime and format it correctly
    # df["payee_due_date"] = pd.to_datetime(df["payee_due_date"], utc=True)

    # Get today's date in UTC for comparison
    today = datetime.now().strftime('%Y-%m-%dT%H:%M:%SZ')

    # Update `payee_payment_status` based on conditions
    df["payee_payment_status"] = df["payee_due_date"].apply(
        lambda x: "due_now" if x == today else "overdue" if x < today else df["payee_payment_status"]
    )
    # Convert postal code to string
    df["payee_postal_code"] = df["payee_postal_code"].astype(str)
    df["payee_phone_number"] = df["payee_phone_number"].astype(str)
    df["payee_added_date_utc"] = df["payee_added_date_utc"].astype(str)
    df = df.fillna("country")

    data = []
    for _, row in df.iterrows():
        try:
            # Convert row to dictionary and validate with Pydantic
            record = Payment(
                payee_first_name=row["payee_first_name"],
                payee_last_name=row["payee_last_name"],
                payee_payment_status=row["payee_payment_status"],
                payee_added_date_utc=row["payee_added_date_utc"],
                payee_due_date=row["payee_due_date"],
                payee_address_line_1=row["payee_address_line_1"],
                payee_address_line_2=row.get("payee_address_line_2"),
                payee_city=row["payee_city"],
                payee_country=row["payee_country"],
                payee_province_or_state=row.get("payee_province_or_state"),
                payee_postal_code=row["payee_postal_code"],
                payee_phone_number=row["payee_phone_number"],
                payee_email=row["payee_email"],
                currency=row["currency"],
                discount_percent=row.get("discount_percent"),
                tax_percent=row.get("tax_percent"),
                due_amount=row["due_amount"]
            )
            data.append(record.dict(by_alias=True))
        except ValidationError as e:
            print(f"Validation failed for row: {row.to_dict()} - {e}")
            
    # Save normalized data into MongoDB
    await MongoDB.db[collection_name].insert_many(data)