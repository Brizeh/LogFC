class Log:
    def __init__(self, url: str):
        self.url         = url
        self.short_name  = url.split("_")[-1]
        self.pjcontent   = None
        self.replay_data = None  # HTML combat-replay data, only fetched for
                                  # bosses that need it (see combat_replay.py)

    def set_pjcontent(self, http_response):
        self.pjcontent = http_response.json()
