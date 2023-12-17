import os
import shutil
import subprocess

LIGHT_MODE = False  # No installation of Librairies in light mode

anki_ext_dir = os.path.join(os.getenv('APPDATA'), 'Anki2', 'addons21', 'ankistreak_test')

if os.path.exists(os.path.join(anki_ext_dir, "test_game")):
    shutil.rmtree(os.path.join(anki_ext_dir, "test_game"))
shutil.copytree("test_game", os.path.join(anki_ext_dir, "test_game"))

if os.path.exists(os.path.join(anki_ext_dir, "__init__.py")):
    os.remove(os.path.join(anki_ext_dir, "__init__.py"))
shutil.copy("__init__.py", anki_ext_dir)

shutil.copy("requirements.txt", anki_ext_dir)

with open(os.path.join(anki_ext_dir, "test_game", "boring", "config.py"), "r") as f:
    lines = f.readlines()
    for i, line in enumerate(lines):
        if "DEBUG" in line:
            lines[i] = "DEBUG = False\n"

with open(os.path.join(anki_ext_dir, "test_game", "boring", "config.py"), "w") as f:
    f.writelines(lines)

for file in os.listdir(os.path.join(anki_ext_dir, "test_game", "game_data")):
    os.remove(os.path.join(anki_ext_dir, "test_game", "game_data", file))

if not LIGHT_MODE:
    subprocess.run(["pip3.9", "install", "-r", "requirements.txt", "--target", '.'], cwd=anki_ext_dir, shell=True)
    os.remove(os.path.join(anki_ext_dir, "demo.py"))

print("Done!")
