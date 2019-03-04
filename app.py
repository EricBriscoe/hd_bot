import configparser
import ast
import os
from tqdm import tqdm
import time
from selenium import webdriver
import re
from deluge_client import DelugeRPCClient


def sync():
    config = configparser.ConfigParser()
    config.read("config.ini")
    shows = config["settings"]["shows"].split(",")
    all_show_dir = config["settings"]["show_dir"]
    print("Shows set to sync:")
    print(type(shows))
    print("Directory for shows")
    print(all_show_dir, "\n")
    if not os.path.isdir(all_show_dir):
        os.mkdir(all_show_dir)

    # Update shows
    dirs = os.listdir(all_show_dir)
    print("Current Show Directories:")
    print(dirs)
    print("Updating Shows:\n")
    for show in shows:
        print("Updating " + show)
        # Create any missing directories
        if show not in dirs:
            os.mkdir(os.path.join(all_show_dir, show))
        show_dir = os.path.join(all_show_dir, show)
        episode_files = os.listdir(show_dir)
        parsed_files = []
        for file in episode_files:
            n = re.findall(" [0-9]+[.]*[0-9]* ")
            parsed_files += n
        show_url = config["settings"]["base_url"] + "/" + show
        episodes = get_episodes(show_url)
        episodes_to_fetch = []
        for e in episodes:
            if e not in parsed_files:
                episodes_to_fetch.append(e)
        links_to_add = get_magnet_links(show_url, episodes_to_fetch)
        if not test_deluge_connection():
            print('error connecting to deluge')
        for link in links_to_add:
            add_to_deluge(link, os.path.join(all_show_dir, show))

def add_to_deluge(link, save_path):
    config = configparser.ConfigParser()
    config.read("config.ini")
    client = DelugeRPCClient(
        config["deluge"]["url"],
        config["deluge"]["port"],
        config["deluge"]["username"],
        config["deluge"]["password"],
    )
    client.connect()
    client.


def test_deluge_connection():
    config = configparser.ConfigParser()
    config.read("config.ini")
    client = DelugeRPCClient(
        config["deluge"]["url"],
        config["deluge"]["port"],
        config["deluge"]["username"],
        config["deluge"]["password"],
    )
    client.connect()
    status = client.connected
    client.disconnect()
    return(status)


def get_magnet_links(show_url, episodes):
    wait_time = 0.2
    episodes = [e.replace(".", "-") for e in episodes]
    config = configparser.ConfigParser()
    config.read("config.ini")
    chromedriver_path = config["settings"]["chromedriver_path"]
    driver = webdriver.Chrome(
        chromedriver_path
    )  # Optional argument, if not specified will search path.
    driver.get(show_url)
    while True:
        try:
            show_more = driver.find_element_by_link_text("Show more ▼")
            show_more.click()
            time.sleep(wait_time)
        except:
            break

    episode_buttons = driver.find_elements_by_class_name("rls-label")
    for button in episode_buttons:
        button.click()
        time.sleep(wait_time)
    magnets = []
    episode_container = driver.find_element_by_class_name("episode-container")
    for ep in episodes:
        try:
            link_container = driver.find_element_by_id(str(ep) + "-1080p")
            link_element = link_container.find_element_by_link_text("Magnet")
            magnets.append(link_element.get_attribute("href"))
        except:
            print("Couldn't find episode " + str(ep))
    print(magnets)
    return magnets
    driver.close()


def get_episodes(show_url):
    wait_time = 0.2
    config = configparser.ConfigParser()
    config.read("config.ini")
    chromedriver_path = config["settings"]["chromedriver_path"]
    driver = webdriver.Chrome(
        chromedriver_path
    )  # Optional argument, if not specified will search path.
    driver.get(show_url)
    # Check for show more, expand if found
    while True:
        try:
            show_more = driver.find_element_by_link_text("Show more ▼")
            show_more.click()
            time.sleep(wait_time)
        except:
            break

    episode_container = driver.find_element_by_class_name("episode-container")
    episodes = re.findall("( [0-9]+[.]*[0-9]* )\w+", episode_container.text)
    episodes = [e.replace(" ", "") for e in episodes]
    driver.close()
    return episodes


def set_config():
    config = configparser.ConfigParser()
    show_dir = os.path.join(os.path.expanduser("~"), "hd_bot_example_dir")
    chromedriver_location = os.path.join(
        os.path.expanduser("~"), "PycharmProjects", "hd_bot", "chromedriver"
    )
    config["settings"] = {
        "base_url": "https://horriblesubs.info/shows/",
        "shows": "one-punch-man,prison-school,goblin-slayer",
        "show_dir": show_dir,
        "chromedriver_path": chromedriver_location,
    }
    config["deluge"] = {
        "url": "127.0.0.1",
        "port": "8080",
        "username": "admin",
        "password": "password",
    }
    with open("config.ini", "w") as configfile:
        config.write(configfile)


if __name__ == "__main__":
    set_config()
    sync()
    # get_episodes("http://horriblesubs.info/shows/goblin-slayer/")
    # get_magnet_links("http://horriblesubs.info/shows/goblin-slayer/", ['01', '02'])
