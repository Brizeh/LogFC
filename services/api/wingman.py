import requests


class WingmanAPI:
    BASE_URL = "https://gw2wingman.nevermindcreations.de/api"

    @staticmethod
    def get_boss_benchmark(boss_id, is_cm=False):
        w_boss_id = boss_id * (-1) ** is_cm
        url = f"{WingmanAPI.BASE_URL}/boss?era=latest&bossID={w_boss_id}"

        response = requests.get(url)
        if not response.ok:
            print(f"Erreur Wingman: {response.status_code}")
            return None

        data = response.json()
        if data.get("error"):
            print(f"Erreur Wingman: {data['error']}")
            return None

        return [data["duration_med"], data["duration_top"]]

    @staticmethod
    def get_percentile(boss_id, is_cm, duration_ms, timestamp):
        url = f"{WingmanAPI.BASE_URL}/getPercentileByMetadata?bossID={boss_id}&isCM={is_cm}&duration={duration_ms}&timestamp={timestamp}"

        response = requests.get(url)
        if not response.ok:
            return None

        data = response.json()
        return data.get("percentile")
