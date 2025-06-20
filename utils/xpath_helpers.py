class XPathHelper:
    BASE_RESULTS_PANEL = "//*[@id='QA0Szd']/div/div/div[1]/div[2]/div/div[1]/div/div/div[1]/div[1]"
    
    BUSINESS_INFO = {
        'name': "//*[@id='QA0Szd']/div/div/div[1]/div[3]/div/div[1]/div/div/div[2]/div[2]/div/div[1]/div[1]/h1",
        'rating': "//*[@id='QA0Szd']/div/div/div[1]/div[3]/div/div[1]/div/div/div[2]//span[@role='img' and contains(@aria-label, 'stars')]", # İş detay panelini hedefleyen daha spesifik rating XPath'i
        'reviews_button': "//*[@id='QA0Szd']/div/div/div[1]/div[3]/div/div[1]/div/div/div[2]/div[3]/div/div/button[2]/div[2]/div[2]",
        'website': "//*[@id='QA0Szd']/div/div/div[1]/div[3]/div/div[1]/div/div/div[2]//a[contains(@aria-label, 'website')]" # İş detay panelini hedefleyen daha spesifik website XPath'i
    }
    
    SCROLL_CONTAINERS = {
        'type1': "//*[@id='QA0Szd']/div/div/div[1]/div[3]/div/div[1]/div/div/div[3]",
        'type2': "//*[@id='QA0Szd']/div/div/div[1]/div[3]/div/div[1]/div/div/div[5]"
    }
    
    @staticmethod
    def get_business_xpath(index):
        div_number = 3 + (index * 2)
        return f"{XPathHelper.BASE_RESULTS_PANEL}/div[{div_number}]/div/a"
    
    @staticmethod
    def get_business_type_xpath(index):
        business_div = 3 + (index * 2)
        return f"{XPathHelper.BASE_RESULTS_PANEL}/div[{business_div}]/div/div[2]/div[5]/div[4]/div/div/a/div"
    
    @staticmethod
    def get_review_xpath(business_type, review_index, base_div_override=None):
        if business_type == 'type1':
            base_div = base_div_override if base_div_override is not None else 9
            container = 3
        else:
            base_div = 10
            container = 5
        
        review_div = 1 + (review_index * 4)
        base_path = f"//*[@id='QA0Szd']/div/div/div[1]/div[3]/div/div[1]/div/div/div[{container}]/div[{base_div}]/div[{review_div}]"
        
        return {
            'reviewer_name': f"{base_path}/div/div/div[2]/div[2]/div[1]/button/div[1]",
            'review_date': f"{base_path}/div/div/div[4]/div[1]/span[2]",
            'photos_container': f"{base_path}/div/div/div[4]/div[3]",
        }
    
    @staticmethod
    def get_review_text_xpath(review_div_id):
        base_xpath = f"//*[@id='{review_div_id}']"
        return {
            'text_span': f"{base_xpath}/span[1]",
            'text_span_alt': f"{base_xpath}/span",
            'more_button': f"{base_xpath}/span/button[@aria-label='See more']"
        }