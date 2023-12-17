import os
import shutil

anki_ext_dir = os.path.join(os.getenv('APPDATA'), 'Anki2', 'addons21', 'ankistreak')
print(anki_ext_dir)

if os.path.exists(os.path.join(anki_ext_dir, "test_game")):
    shutil.rmtree(os.path.join(anki_ext_dir, "test_game"))
shutil.copytree("test_game", os.path.join(anki_ext_dir, "test_game"))

if os.path.exists(os.path.join(anki_ext_dir, "__init__.py")):
    os.remove(os.path.join(anki_ext_dir, "__init__.py"))
shutil.copy("__init__.py", anki_ext_dir)

# change debug to false
with open(os.path.join(anki_ext_dir, "test_game", "boring", "config.py"), "r") as f:
    lines = f.readlines()
    for i, line in enumerate(lines):
        if "DEBUG" in line:
            lines[i] = "DEBUG = False\n"

with open(os.path.join(anki_ext_dir, "test_game", "boring", "config.py"), "w") as f:
    f.writelines(lines)

# removes the saves in the game_data directory without removing the directory
for file in os.listdir(os.path.join(anki_ext_dir, "test_game", "game_data")):
    os.remove(os.path.join(anki_ext_dir, "test_game", "game_data", file))
