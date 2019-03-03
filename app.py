import configparser
import ast
import os
from tqdm import tqdm
from urllib.request import urlopen

def sync():
    config = configparser.ConfigParser()
    config.read("config.ini")
    shows = config["settings"]["shows"].split(",")
    all_show_dir = config["settings"]["show_dir"]
    print('Shows set to sync:')
    print(type(shows))
    print('Directory for shows')
    print(all_show_dir, '\n')
    if not os.path.isdir(all_show_dir):
        os.mkdir(all_show_dir)

    # Update shows
    dirs = os.listdir(all_show_dir)
    print('Current Show Directories:')
    print(dirs)
    print('Updating Shows:\n')
    for show in tqdm(shows):
        # Create any missing directories
        if show not in dirs:
            os.mkdir(os.path.join(all_show_dir, show))
        show_dir = os.path.join(all_show_dir, show)
        episode_files = os.listdir(show_dir)
        show_url = config["settings"]["base_url"] + "/show"

        break


def set_config():
    config = configparser.ConfigParser()
    show_dir = os.path.join(os.path.expanduser('~'), 'hd_bot_example_dir')
    config["settings"] = {
        "base_url": "https://horriblesubs.info/shows/",
        "shows": "one-punch-man,prison-school,goblin-slayer",
        "show_dir": show_dir
    }
    with open("config.ini", "w") as configfile:
        config.write(configfile)


if __name__ == "__main__":
    set_config()
    sync()
