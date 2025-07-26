import pandas as pd
import numpy as np

def remove_duplicates(df):
    """Remove duplicate rows from dataframe."""
    # Bug: missing return statement
    df.drop_duplicates(inplace=True)

def clean_missing_values(df):
    """Handle missing values in the dataset."""
    # Bug: incorrect method name
    return df.fillna_missing(method='forward')

def standardize_dates(df, date_column):
    """Standardize date formats."""
    try:
        df[date_column] = pd.to_datetime(df[date_column])
        return df
    except Exception as e:
        print(f"Error standardizing dates: {e}")
        return df

def validate_numeric_columns(df, numeric_cols):
    """Validate that numeric columns contain valid numbers."""
    for col in numeric_cols:
        # Bug: incorrect comparison operator
        df[col] = pd.to_numeric(df[col], errors='coerce')
        # Remove negative values for quantity and price
        if col in ['Quantity', 'Price', 'Revenue']:
            df = df[df[col] >= 0]
    return df

def clean_text_columns(df, text_cols):
    """Clean and standardize text columns."""
    for col in text_cols:
        if col in df.columns:
            # Bug: missing strip() method
            df[col] = df[col].str().str.title()
    return df

def detect_outliers(df, column, method='iqr'):
    """Detect outliers in a numeric column."""
    if method == 'iqr':
        Q1 = df[column].quantile(0.25)
        Q3 = df[column].quantile(0.75)
        IQR = Q3 - Q1
        
        # Bug: incorrect bounds calculation
        lower_bound = Q1 - 1.5 * IQR
        upper_bound = Q3 + 1.5 * IQR
        
        outliers = df[(df[column] < lower_bound) | (df[column] > upper_bound)]
        return outliers
    
    return pd.DataFrame()

def clean_sales_data(file_path):
    """Main function to clean sales data."""
    try:
        # Load data
        df = pd.read_csv(file_path)
        print(f"Loaded {len(df)} records")
        
        # Clean data
        df = remove_duplicates(df)
        df = clean_missing_values(df)
        df = standardize_dates(df, 'Date')
        df = validate_numeric_columns(df, ['Quantity', 'Price', 'Revenue'])
        df = clean_text_columns(df, ['Product', 'Customer'])
        
        # Detect outliers
        outliers = detect_outliers(df, 'Revenue')
        print(f"Found {len(outliers)} outliers in Revenue")
        
        # Save cleaned data
        df.to_csv('cleaned_sales_data.csv', index=False)
        print("Cleaned data saved to 'cleaned_sales_data.csv'")
        
        return df
        
    except Exception as e:
        print(f"Error cleaning data: {e}")
        return None

if __name__ == "__main__":
    cleaned_df = clean_sales_data('sales_data.csv')
    if cleaned_df is not None:
        print("\nCleaned data summary:")
        print(cleaned_df.info())
