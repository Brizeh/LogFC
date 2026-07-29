import json

class Log:
    def __init__(self, url: str):
        self.url        = url
        self.short_name = url.split("_")[-1]
        self.jcontent   = None
        self.pjcontent  = None
    
    def set_jcontent(self, http_response):       
        content        = http_response.content.decode("utf-8")
        try:
            java_data_text = content.split('var _logData = ')[1].split('var logData = _logData;')[0].rsplit(';', 1)[0].strip()
            parsed = json.loads(java_data_text)
            self.jcontent = parsed
        except:
            try:
                logData = content.split('const _logData = ')[1].split('const _crData =')[0].rsplit(';', 1)[0].strip()
                crData = content.split('const _crData = ')[1].split('const _graphData =')[0].rsplit(';', 1)[0].strip()
                graphData = content.split('const _graphData = ')[1].split('const _healingStatsExtension =')[0].rsplit(';', 1)[0].strip()
                jlogData = json.loads(logData)
                jcrData = json.loads(crData)
                jgraphData = json.loads(graphData)
                jlogData["crData"] = jcrData
                jlogData["graphData"] = jgraphData
                self.jcontent = jlogData
            except:
                print(f"Parsed Error : {self.url}")

    def set_pjcontent(self, http_response):
        self.pjcontent = http_response.json()