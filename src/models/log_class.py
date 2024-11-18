import requests
import json
 
class Log:
    def __init__(self, url: str):
        self.url       = url
        self.content   = self.get_html()
        self.jcontent  = self.get_parsed_json()
        self.pjcontent = self.get_not_parsed_json()
        self.create_boss()

    def get_html(self):        
        with requests.Session() as session:
            html_text = session.get(self.url).content.decode("utf-8")
        return html_text

    def get_parsed_json(self):     
        java_data_text = self.content.split('var _logData = ')[1].split('var logData = _logData;')[0].rsplit(';', 1)[0].strip()
        json_content   = json.loads(java_data_text)
        return json_content
    
    def get_not_parsed_json(self):
        requestUrl = f"https://dps.report/getJson?permalink={self.url}"
        return requests.get(requestUrl).json()

    def create_boss(self):
        from models.boss_facto import BossFactory  # Import moved here to avoid circular import
        BossFactory.create_boss(self)