import pandas as pd
from datetime import datetime
import os
import re


class DataSaver:
    def __init__(self):
        self.data_dir = "data"
        self.business_filename = "business_info.xlsx"
        self.reviews_filename = "reviews.xlsx"
        self.ensure_data_directory()

    def ensure_data_directory(self):
        if not os.path.exists(self.data_dir):
            os.makedirs(self.data_dir)
            print("[INFO] Created data directory: {}".format(self.data_dir))

    def save_business_info(self, business_data):
        try:
            filepath = os.path.join(self.data_dir, self.business_filename)

            df_data = pd.DataFrame([{
                "Business Name": business_data.get("business_name"),
                "Rating": business_data.get("rating"),
                "Address": business_data.get("address"),
                "Phone": business_data.get("phone"),
                "Website": business_data.get("website"),
                "Maps URL": business_data.get("maps_url"),
                "Scraped At": business_data.get("scraped_at"),
            }])

            if os.path.exists(filepath):
                with pd.ExcelWriter(filepath, mode='a', engine='openpyxl', if_sheet_exists='overlay') as writer:
                    df_data.to_excel(writer, index=False, header=False, startrow=writer.sheets['Sheet1'].max_row)
            else:
                df_data.to_excel(filepath, index=False)
            print("[INFO] Business info saved to: {}".format(self.business_filename))
            return filepath

        except Exception as e:
            print("[ERROR] Failed to save business info: {}".format(str(e)))
            return None

    def save_reviews(self, reviews_data):
        try:
            if not reviews_data or not reviews_data.get("reviews"):
                print("[INFO] No reviews data to save")
                return None

            filepath = os.path.join(self.data_dir, self.reviews_filename)

            df_data = []
            business_name = reviews_data.get("business_name", "Unknown Business")
            scraped_at = reviews_data.get(
                "scraped_at", datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            )

            for review in reviews_data.get("reviews", []):
                if not review.get("reviewer_name"):
                    continue

                photo_urls = ", ".join(review.get("photos", []))
                review_text = review.get("review_text", "").strip()

                df_data.append(
                    {
                        "Business Name": business_name,
                        "Reviewer Name": review.get("reviewer_name", ""),
                        "Review Text": review_text,
                        "Review Date": review.get("review_date", ""),
                        "Photo URLs": photo_urls,
                        "Scraped At": scraped_at,
                    }
                )

            if df_data:
                df = pd.DataFrame(df_data)

                if os.path.exists(filepath):
                    with pd.ExcelWriter(filepath, mode='a', engine='openpyxl', if_sheet_exists='overlay') as writer:
                        df.to_excel(writer, index=False, header=False, startrow=writer.sheets['Sheet1'].max_row)
                else:
                    df.to_excel(filepath, index=False)
                print("[INFO] {} reviews saved to: {}".format(len(df_data), self.reviews_filename))
                return filepath
            else:
                print("[INFO] No valid reviews to save")
                return None

        except Exception as e:
            print("[ERROR] Failed to save reviews: {}".format(str(e)))
            return None
