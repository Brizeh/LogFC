from const import CUSTOM_NAMES, ALL_MECHS

class Player:
    def __init__(self, boss, account: str):
        self.boss                   = [boss]
        self.account                = account
        self.name                   = account[:-5]
        self.nickname               = self.get_nickname()
        self.mvps                   = 0
        self.lvps                   = 0
        self.boxWins                = None
        self.dps_marks: list[float] = []
        self.player_mechs           = self.init_mechs()
        
    def init_mechs(self):
        allmechs = {}
        for category, mechs in ALL_MECHS.items():
            allmechs[category] = {}
            for mech, description in mechs.items():
                allmechs[category][mech] = {"value": 0, "description": description, "presence": 0}
        return allmechs
    
    def add_boss(self, boss) -> None:
        self.boss.append(boss)
        self.boss.sort(key=lambda boss: boss.start_date, reverse=False)
        
    def get_boss_names(self) -> list[str]:
        return [bos.name for bos in self.boss]
        
    def get_mvps(self) -> str:
        return f"Titres MVP de {self.name} : {self.mvps}"

    def get_lvps(self) -> str:
        return f"Titres LVP de {self.name} : {self.lvps}"

    def add_mark(self, mark: float) -> None:
        self.dps_marks.append(mark)

    def get_mark(self) -> float:
        if self.dps_marks:
            return sum(self.dps_marks) / len(self.dps_marks)
        return None
    
    def get_nickname(self):
        nickname = CUSTOM_NAMES.get(self.account)
        if nickname:
            return nickname
        else:
            return self.account
