"""
Process RavenStack and Chioma CSV files
"""
import pandas as pd
import os
from pathlib import Path

# Define paths
BASE_DIR = Path(__file__).resolve().parent.parent.parent.parent
RAW_DATA_DIR = BASE_DIR / "data" / "raw"
PROCESSED_DATA_DIR = BASE_DIR / "data" / "processed"

# Ensure processed directory exists
PROCESSED_DATA_DIR.mkdir(parents=True, exist_ok=True)


def process_ravenstack_data():
    """Process all RavenStack CSV files"""
    print("Processing RavenStack data...")
    
    # Load RavenStack files
    accounts = pd.read_csv(RAW_DATA_DIR / "ravenstack_accounts.csv")
    churn_events = pd.read_csv(RAW_DATA_DIR / "ravenstack_churn_events.csv")
    feature_usage = pd.read_csv(RAW_DATA_DIR / "ravenstack_feature_usage.csv")
    subscriptions = pd.read_csv(RAW_DATA_DIR / "ravenstack_subscriptions.csv")
    support_tickets = pd.read_csv(RAW_DATA_DIR / "ravenstack_support_tickets.csv")
    
    print(f"✓ Loaded accounts: {len(accounts)} rows")
    print(f"✓ Loaded churn events: {len(churn_events)} rows")
    print(f"✓ Loaded feature usage: {len(feature_usage)} rows")
    print(f"✓ Loaded subscriptions: {len(subscriptions)} rows")
    print(f"✓ Loaded support tickets: {len(support_tickets)} rows")
    
    # Save processed files
    accounts.to_csv(PROCESSED_DATA_DIR / "ravenstack_accounts_processed.csv", index=False)
    churn_events.to_csv(PROCESSED_DATA_DIR / "ravenstack_churn_processed.csv", index=False)
    feature_usage.to_csv(PROCESSED_DATA_DIR / "ravenstack_usage_processed.csv", index=False)
    subscriptions.to_csv(PROCESSED_DATA_DIR / "ravenstack_subscriptions_processed.csv", index=False)
    support_tickets.to_csv(PROCESSED_DATA_DIR / "ravenstack_tickets_processed.csv", index=False)
    
    print("✓ RavenStack data processed successfully!\n")
    return {
        "accounts": accounts,
        "churn": churn_events,
        "usage": feature_usage,
        "subscriptions": subscriptions,
        "tickets": support_tickets
    }


def process_chioma_data():
    """Process Chioma's sales funnel data"""
    print("Processing Chioma sales funnel data...")
    
    sales_funnel = pd.read_csv(RAW_DATA_DIR / "Chioma_Iwuchukwu-Sales_Funnel_Revenue_Forecast.csv - sales_funnel.csv")
    
    print(f"✓ Loaded sales funnel: {len(sales_funnel)} rows")
    print(f"✓ Columns: {list(sales_funnel.columns)}")
    
    # Save processed file
    sales_funnel.to_csv(PROCESSED_DATA_DIR / "chioma_sales_funnel_processed.csv", index=False)
    
    print("✓ Chioma data processed successfully!\n")
    return sales_funnel


def main():
    """Main processing function"""
    print("=" * 60)
    print("Starting Data Processing Pipeline")
    print("=" * 60 + "\n")
    
    # Process RavenStack data
    ravenstack_data = process_ravenstack_data()
    
    # Process Chioma data
    chioma_data = process_chioma_data()
    
    print("=" * 60)
    print("✓ All data processed successfully!")
    print(f"✓ Processed files saved to: {PROCESSED_DATA_DIR}")
    print("=" * 60)


if __name__ == "__main__":
    main()