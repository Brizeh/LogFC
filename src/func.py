import math
from datetime import timedelta

from .const import CUSTOM_NAMES, EMOTE_WINGMAN
from .languages import LANGUES

def time_to_index(time: int, base):  # time in millisecond
    return int(time / base)

def get_dist(pos1: list[float], pos2: list[float]):
    x1, y1 = pos1[0], pos1[1]
    x2, y2 = pos2[0], pos2[1]
    return math.hypot(x1 - x2, y1 - y2)

def disp_time(td: timedelta):
    days, seconds = td.days, td.seconds
    hours = seconds // 3600
    minutes = (seconds // 60) % 60
    seconds = seconds % 60
    if days:
        return f"{days}d{hours:02}h{minutes:02}m{seconds:02}s"
    elif hours:
        return f"{hours}h{minutes:02}m{seconds:02}s"
    elif minutes:
        return f"{minutes}m{seconds:02}s"
    else:
        return f"{seconds}s"

def get_message_reward(analysis):
    logs    = analysis.bosses
    players = analysis.players
    titre   = analysis.title
    if not logs:
        print("No boss found")
        return []

    def cut_text(text):
        run_message_length = len(text)
        if run_message_length >= cutting_text_limit:
            split_message.append(text)
            return ""
        return text

    cutting_text_limit = 1700

    mvp = []
    lvp = []
    max_mvp_score = 1
    max_lvp_score = 1

    for player in players.values():
        if player.mvps > max_mvp_score:
            max_mvp_score = player.mvps
            mvp = [player]
        elif player.mvps == max_mvp_score:
            mvp.append(player)
        if player.lvps > max_lvp_score:
            max_lvp_score = player.lvps
            lvp = [player]
        elif player.lvps == max_lvp_score:
            lvp.append(player)

    mvp_names = []
    lvp_names = []
    
    for player in mvp:
        account = player.account
        custom_name = CUSTOM_NAMES.get(account)
        if custom_name:
            if type(custom_name) == str:
                mvp_names.append(custom_name)
            else:
                discord_name = custom_name.get("discord")
                if discord_name:
                    mvp_names.append(discord_name)
                else:
                    mvp_names.append(custom_name.get("nickname"))
        else:
            mvp_names.append(player.name)
            
    for player in lvp:
        account = player.account
        custom_name = CUSTOM_NAMES.get(account)
        if custom_name:
            if type(custom_name) == str:
                lvp_names.append(custom_name)
            else:
                discord_name = custom_name.get("discord")
                if discord_name:
                    lvp_names.append(discord_name)
                else:
                    lvp_names.append(custom_name.get("nickname"))
        else:
            lvp_names.append(player.name)

    logs.sort(key=lambda log: log.start_date, reverse=False)
    wings = {}
    for log in logs:
        _wing = log.wing
        if wings.get(_wing):
            wings[_wing].append(log)
        else:
            wings[_wing] = [log]

    run_date = logs[0].start_date.strftime("%d/%m/%Y")
    run_duration = disp_time(logs[-1].end_date - logs[0].start_date)
    number_boss = len(logs)

    run_message = f"# {titre}\n" if number_boss > 2 else ""
    run_message += f"# {run_date}\n"
    
    split_message = []
    total_wingman_score = 0
    notes_nb = 0
    for wingname, wing in wings.items():
        wing_first_log = wing[0]
        wing_last_log = wing[-1]
        wing_duration = disp_time(wing_last_log.end_date - wing_first_log.start_date)

        if type(wingname) == int: 
            if wingname == 1:
                run_message += LANGUES["selected_language"]["W1"].format(wing_duration=wing_duration)
                
            elif wingname == 3:
                escort_in_run = any(boss.name == "ESCORT" for boss in wing)
                if escort_in_run:
                    run_message += f"## W3 - *{wing_duration}*\n"
                else:
                    run_message += LANGUES["selected_language"]["W3"].format(wing_duration=wing_duration)
                    
            elif wingname == 7:
                run_message += LANGUES["selected_language"]["W7"].format(wing_duration=wing_duration)
                
            else:
                run_message += f"## W{wingname} - *{wing_duration}*\n"    
                  
        else:
            run_message += LANGUES["selected_language"][wingname].format(wing_duration=wing_duration)
        
        for boss in wing:
            boss_name      = boss.name + (" CM" if boss.cm else "")
            boss_duration  = disp_time(timedelta(seconds=boss.duration_ms / 1000))
            boss_url       = boss.log.url
            boss_percentil = boss.wingman_percentile
            # un boss cree sans passer par InputParser n'a pas de doublons
            # connus : on compte alors zero fail plutot que de planter
            fail_count = len(analysis.dups.get(boss.log.short_name, [boss.log.url]))-1
            fail_msg       = ""
            if fail_count:
                fail_msg = f" *{fail_count} fails* :x:"
            if boss_percentil is not None:
                notes_nb += 1
                total_wingman_score += boss_percentil
                run_message += f"* **[{boss_name}]({boss_url})** **{boss_duration} ({boss_percentil}%{EMOTE_WINGMAN})**"
            else:
                run_message += f"* **[{boss_name}]({boss_url})** **{boss_duration}**"
            if boss.name in ["BONESKINNER", "WOJ", "FRAENIR", "KODANS", "ICEBROOD"]:
                if boss.duration_ms < 180000:
                    run_message += " :first_place:"
                elif boss.duration_ms < 300000:
                    run_message += " :second_place:"
                else:
                    run_message += " :third_place:"
            run_message += f"{fail_msg}\n"
            run_message = cut_text(run_message)

            for mvp in boss.mvp:
                if mvp:
                    run_message += mvp + "\n"
                    run_message = cut_text(run_message)
            for lvp in boss.lvp:
                if lvp:
                    run_message += lvp + "\n"
                    run_message = cut_text(run_message)
            if boss.box:
                run_message += boss.box + "\n"
                run_message = cut_text(run_message)
            if boss.name != "ESCORT":
                for player_account, dps_mark in boss.get_dps_ranking().items():
                    players[player_account].add_mark(dps_mark)

        run_message += "\n"

    if number_boss > 2:
        mvps = ', '.join(mvp_names)
        lvps = ', '.join(lvp_names)
        note_wingman = None
        if notes_nb:
            note_wingman = total_wingman_score / notes_nb
        if max_mvp_score > 1:
            run_message += LANGUES["selected_language"]["MVP"].format(mvps=mvps, max_mvp_score=max_mvp_score)
        if max_lvp_score > 1:
            run_message += LANGUES["selected_language"]["LVP"].format(lvps=lvps, max_lvp_score=max_lvp_score)
        run_message += LANGUES["selected_language"]["TIME"].format(run_duration=run_duration)
        if note_wingman:
            run_message += LANGUES["selected_language"]["WINGMAN"].format(note_wingman=note_wingman, emote_wingman=EMOTE_WINGMAN)

    
    """player_rankings = list(filter(
        lambda x: x[1] is not None,
        [(player.account, player.get_mark()) for player in players.values()]
    ))
    player_rankings.sort(key=lambda r: r[1], reverse=True)
    for r in player_rankings:
        run_message += f"\n{r[0]} a la note moyenne de {r[1]:0.2f}/20 en dps"
    """
    
    
    boxers = []
    for account, player in players.items():
        if player.boxWins is not None:
            boxers.append(player)
    if boxers:
        if boxers[0].boxWins > boxers[1].boxWins:
            run_message += f"# :boxing_gloves: {boxers[0].nickname} a battu {boxers[1].nickname} :boxing_gloves:\n"
            run_message += f"# {boxers[0].boxWins} : {boxers[1].boxWins}"
        if boxers[0].boxWins < boxers[1].boxWins:
            run_message += f"# :boxing_gloves: {boxers[1].nickname} a battu {boxers[0].nickname} :boxing_gloves:\n"
            run_message += f"# {boxers[1].boxWins} : {boxers[0].boxWins}"
        if boxers[0].boxWins == boxers[1].boxWins:
            run_message += f"# :boxing_gloves: {boxers[0].nickname} ex æquo {boxers[1].nickname} Nous dormissâmes :boxing_gloves:\n"
            run_message += f"# {boxers[0].boxWins} : {boxers[1].boxWins}"
    run_message = cut_text(run_message)
    split_message.append(run_message)

    return split_message
