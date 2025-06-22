import pandas as pd
import os
import gc
from datetime import datetime

class ExcelManager:
    def __init__(self):
        self.business_file = 'business_data.xlsx'
        self.reviews_file = 'reviews_data.xlsx'
    
    def save_businesses_to_excel(self, business_data_batch):
        try:
            df = pd.DataFrame(business_data_batch)
            
            if os.path.exists(self.business_file):
                existing_df = pd.read_excel(self.business_file)
                df = pd.concat([existing_df, df], ignore_index=True)
            
            df.to_excel(self.business_file, index=False)
            
            del df
            if 'existing_df' in locals():
                del existing_df
            gc.collect()
            
        except Exception as e:
            raise Exception(f"Failed to save business data: {str(e)}")
    
    def save_reviews_to_excel(self, reviews_data, business_name="Unknown"):
        try:
            if not reviews_data:
                return
            
            for review in reviews_data:
                review['business_name'] = business_name
            
            df = pd.DataFrame(reviews_data)
            df['extraction_timestamp'] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            
            if os.path.exists(self.reviews_file):
                existing_df = pd.read_excel(self.reviews_file)
                df = pd.concat([existing_df, df], ignore_index=True)
            
            df.to_excel(self.reviews_file, index=False)
            
            del df
            if 'existing_df' in locals():
                del existing_df
            gc.collect()
            
        except Exception as e:
            raise Exception(f"Failed to save reviews data: {str(e)}")