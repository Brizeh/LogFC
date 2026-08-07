class Log:
    def __init__(self, url: str):
        self.url        = url
        self.short_name = url.split("_")[-1]
        self.pjcontent  = None

    def set_pjcontent(self, http_response):
        self.pjcontent = http_response.json()
