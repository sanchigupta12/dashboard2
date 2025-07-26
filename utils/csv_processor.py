import pandas as pd
import numpy as np
from io import StringIO

class CSVProcessor:
    """Utility class for processing CSV files"""
    
    def __init__(self):
        self.supported_encodings = ['utf-8', 'latin1', 'cp1252', 'iso-8859-1']
    
    def load_csv(self, uploaded_file):
        """Load and process uploaded CSV file with error handling"""
        
        # Try different encodings
        for encoding in self.supported_encodings:
            try:
                # Reset file pointer
                uploaded_file.seek(0)
                
                # Read file content
                content = uploaded_file.read()
                
                # Convert bytes to string if necessary
                if isinstance(content, bytes):
                    content = content.decode(encoding)
                
                # Create StringIO object for pandas
                csv_buffer = StringIO(content)
                
                # Try to read CSV with different parameters
                df = self._try_csv_read(csv_buffer)
                
                if df is not None and not df.empty:
                    # Clean and process the dataframe
                    df = self._clean_dataframe(df)
                    return df
                    
            except Exception as e:
                print(f"Failed to read with encoding {encoding}: {e}")
                continue
        
        raise ValueError("Could not read CSV file with any supported encoding")
    
    def _try_csv_read(self, csv_buffer):
        """Try different CSV reading parameters"""
        
        # Common CSV reading configurations
        configs = [
            {'sep': ',', 'encoding': None},
            {'sep': ';', 'encoding': None},
            {'sep': '\t', 'encoding': None},
            {'sep': ',', 'encoding': None, 'quotechar': '"'},
            {'sep': ',', 'encoding': None, 'quotechar': "'"},
        ]
        
        for config in configs:
            try:
                csv_buffer.seek(0)
                df = pd.read_csv(csv_buffer, **config)
                
                # Validate the dataframe
                if self._validate_dataframe(df):
                    return df
                    
            except Exception as e:
                print(f"CSV read attempt failed with config {config}: {e}")
                continue
        
        return None
    
    def _validate_dataframe(self, df):
        """Validate that the dataframe is reasonable"""
        
        # Check if dataframe is not empty
        if df.empty:
            return False
        
        # Check if we have reasonable number of columns (not too many, not too few)
        if len(df.columns) < 1 or len(df.columns) > 100:
            return False
        
        # Check that we don't have too many missing values
        if df.isnull().sum().sum() / df.size > 0.9:
            return False
        
        return True
    
    def _clean_dataframe(self, df):
        """Clean and preprocess the dataframe"""
        
        # Clean column names
        df.columns = df.columns.astype(str)
        df.columns = [col.strip() for col in df.columns]
        
        # Remove completely empty rows and columns
        df = df.dropna(how='all')  # Remove rows where all values are NaN
        df = df.dropna(axis=1, how='all')  # Remove columns where all values are NaN
        
        # Convert obvious numeric columns
        df = self._convert_numeric_columns(df)
        
        # Convert obvious date columns
        df = self._convert_date_columns(df)
        
        # Handle duplicate column names
        df = self._handle_duplicate_columns(df)
        
        return df
    
    def _convert_numeric_columns(self, df):
        """Convert columns that should be numeric"""
        
        for col in df.columns:
            # Skip if already numeric
            if pd.api.types.is_numeric_dtype(df[col]):
                continue
            
            # Try to convert to numeric
            # First, clean common non-numeric characters
            if df[col].dtype == 'object':
                # Remove currency symbols, commas, whitespace
                cleaned_series = df[col].astype(str).str.replace('[$,\s]', '', regex=True)
                cleaned_series = cleaned_series.replace(['', 'nan', 'NaN', 'null'], np.nan)
                
                # Try conversion
                try:
                    numeric_series = pd.to_numeric(cleaned_series, errors='coerce')
                    
                    # If more than 50% of non-null values can be converted, assume it's numeric
                    non_null_count = len(cleaned_series.dropna())
                    converted_count = len(numeric_series.dropna())
                    
                    if non_null_count > 0 and (converted_count / non_null_count) > 0.5:
                        df[col] = numeric_series
                        
                except Exception:
                    pass  # Keep as original type
        
        return df
    
    def _convert_date_columns(self, df):
        """Convert columns that might be dates"""
        
        date_keywords = ['date', 'time', 'created', 'updated', 'timestamp']
        
        for col in df.columns:
            col_lower = col.lower()
            
            # Check if column name suggests it's a date
            if any(keyword in col_lower for keyword in date_keywords):
                try:
                    df[col] = pd.to_datetime(df[col], errors='coerce')
                except Exception:
                    pass  # Keep as original type
        
        return df
    
    def _handle_duplicate_columns(self, df):
        """Handle duplicate column names"""
        
        cols = pd.Series(df.columns)
        
        # Find duplicates
        duplicated_mask = cols.duplicated()
        duplicated_cols = cols[duplicated_mask].drop_duplicates().tolist()
        
        for dup_col in duplicated_cols:
            # Get indices of duplicate columns
            dup_indices = cols[cols == dup_col].index.tolist()
            
            # Rename duplicates with suffix
            dup_indices_list = list(dup_indices)
            for i, idx in enumerate(dup_indices_list[1:], 1):
                cols.iloc[idx] = f"{dup_col}_{i}"
        
        df.columns = cols
        return df
    
    def get_file_info(self, df):
        """Get basic information about the processed file"""
        
        info = {
            'shape': df.shape,
            'columns': list(df.columns),
            'dtypes': df.dtypes.to_dict(),
            'memory_usage': df.memory_usage(deep=True).sum(),
            'missing_values': df.isnull().sum().to_dict()
        }
        
        return info
