import datetime
import json
import os.path
import sys

import aqt.utils
from aqt import gui_hooks, mw

sys.path.append(os.path.dirname(__file__))
import test_game.main

cwd = os.path.dirname(__file__)
today_ord = datetime.date.today().toordinal() + 1  #


def get_streak() -> tuple[int, int]:
    if not mw.col.conf.get("streak"):
        return 0, today_ord

    today_ordinal = today_ord
    streak, last_day_ordinal = mw.col.conf["streak"]

    if today_ordinal == last_day_ordinal:
        pass
    elif today_ordinal == last_day_ordinal + 1:
        streak += 1
    else:
        streak = 1
    return streak, today_ordinal


def enhance_numbers(n):
    if n == 1:
        return "1st"
    elif n == 2:
        return "2nd"
    elif n == 3:
        return "3rd"
    else:
        return f"{n}th"


anki_data_path = os.path.join(cwd, "anki_data.json")


# requires arguments a, b, c because of how Anki calls the hook
def process_file(a, b, c):
    # get today's ordinal date
    today_ordinal = datetime.date.today().toordinal()
    anki_data = json.load(open(anki_data_path))

    if not "time_ordinal" in anki_data or anki_data["time_ordinal"] != today_ordinal:
        anki_data["time_ordinal"] = today_ordinal
        anki_data["nb_cards_learned_today"] = 1
    else:
        anki_data["nb_cards_learned_today"] += 1

    json.dump(anki_data, open(anki_data_path, "w"))


### Add a button to the main screen with title "start game" and that starts the game when clicked
def start_game():
    test_game.main.main()


def on_profile_open():
    aqt.utils.showInfo("Welcome back !")

    previous_streak, _ = mw.col.conf.get("streak", (0, 0))
    mw.col.conf["streak"] = get_streak()
    streak, ordinal = mw.col.conf["streak"]
    if streak > previous_streak:
        aqt.utils.showInfo(f"This is your {enhance_numbers(streak)} day in a row !\nKeep it up !")

    # retrieve number of cards to learn today
    due_tree = mw.col.sched.deck_due_tree()
    to_review = due_tree.review_count + due_tree.learn_count + due_tree.new_count

    aqt.utils.showInfo(f"You have {to_review} cards to learn today. Good luck !")
    # write max number of cards to learn today to the json (anki_data.json)
    json.dump({"nb_cards_to_review_today": to_review}, open(anki_data_path, "w"))
    start_game()


gui_hooks.profile_did_open.append(on_profile_open)
gui_hooks.reviewer_did_answer_card.append(process_file)

action = aqt.qt.QAction("Start game", mw)
action.triggered.connect(start_game)
mw.form.menuTools.addAction(action)
