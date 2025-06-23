import pandas as pd
import os
from datetime import datetime
from typing import List, Dict, Any, Optional

class ExcelManager:
    def __init__(self, business_file: str = None, reviews_file: str = None):
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        self.business_file = business_file or f'business_data_{timestamp}.xlsx'
        self.reviews_file = reviews_file or f'reviews_data_{timestamp}.xlsx'
        self._validate_file_paths()
    
    def _validate_file_paths(self) -> None:
        for file_path in [self.business_file, self.reviews_file]:
            directory = os.path.dirname(file_path) if os.path.dirname(file_path) else '.'
            if not os.access(directory, os.W_OK):
                raise PermissionError(f"No write permission for directory: {directory}")
    
    def _ensure_file_accessible(self, file_path: str) -> None:
        if os.path.exists(file_path):
            if not os.access(file_path, os.R_OK | os.W_OK):
                raise PermissionError(f"No read/write permission for file: {file_path}")
    
    def _safe_dataframe_creation(self, data: List[Dict[str, Any]]) -> pd.DataFrame:
        if not data:
            raise ValueError("Cannot create DataFrame from empty data")
        
        return pd.DataFrame(data)
    
    def _safe_excel_read(self, file_path: str) -> Optional[pd.DataFrame]:
        try:
            self._ensure_file_accessible(file_path)
            return pd.read_excel(file_path)
        except FileNotFoundError:
            return None
        except PermissionError:
            raise
        except Exception as e:
            raise RuntimeError(f"Failed to read Excel file {file_path}: {e}") from e
    
    def _safe_excel_write(self, df: pd.DataFrame, file_path: str) -> None:
        if df.empty:
            raise ValueError("Cannot write empty DataFrame to Excel")
        
        try:
            df.to_excel(file_path, index=False)
        except Exception as e:
            raise RuntimeError(f"Failed to write Excel file {file_path}: {e}") from e
    
    def save_businesses_to_excel(self, business_data_batch: List[Dict[str, Any]]) -> None:
        if not business_data_batch:
            raise ValueError("Business data batch cannot be empty")
        
        try:
            new_df = self._safe_dataframe_creation(business_data_batch)
            existing_df = self._safe_excel_read(self.business_file)
            
            if existing_df is not None:
                old_count = len(existing_df)
                combined_df = pd.concat([existing_df, new_df], ignore_index=True)
                new_total = len(combined_df)
                print(f"[EXCEL] Added {len(new_df)} businesses to {self.business_file}. Total: {old_count} -> {new_total}")
            else:
                combined_df = new_df
                print(f"[EXCEL] Created new file {self.business_file} with {len(new_df)} businesses")
            
            self._safe_excel_write(combined_df, self.business_file)
            
        except Exception as e:
            raise RuntimeError(f"Failed to save business data: {e}") from e
    
    def save_reviews_to_excel(self, reviews_data: List[Dict[str, Any]], business_name: str = "Unknown") -> None:
        if not reviews_data:
            return
        
        if not isinstance(business_name, str) or not business_name.strip():
            business_name = "Unknown"
        
        try:
            enriched_reviews = []
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            
            for review in reviews_data:
                if not isinstance(review, dict):
                    continue
                
                enriched_review = review.copy()
                enriched_review['business_name'] = business_name
                enriched_review['extraction_timestamp'] = timestamp
                enriched_reviews.append(enriched_review)
            
            if not enriched_reviews:
                return
            
            new_df = self._safe_dataframe_creation(enriched_reviews)
            existing_df = self._safe_excel_read(self.reviews_file)
            
            if existing_df is not None:
                old_count = len(existing_df)
                combined_df = pd.concat([existing_df, new_df], ignore_index=True)
                new_total = len(combined_df)
                print(f"[EXCEL] Added {len(new_df)} reviews for '{business_name}' to {self.reviews_file}. Total: {old_count} -> {new_total}")
            else:
                combined_df = new_df
                print(f"[EXCEL] Created new reviews file {self.reviews_file} with {len(new_df)} reviews for '{business_name}'")
            
            self._safe_excel_write(combined_df, self.reviews_file)
            
        except Exception as e:
            raise RuntimeError(f"Failed to save reviews data: {e}") from e