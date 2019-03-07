import configparser
import os
import re
import time

from tqdm import tqdm
from selenium import webdriver
from selenium.common.exceptions import NoSuchElementException, ElementNotVisibleException, WebDriverException


def sync():
    config = configparser.ConfigParser()
    config.read("config.ini")
    shows = config["settings"]["shows"].split(",")
    all_show_dir = config["settings"]["show_dir"]
    print("Shows set to sync:")
    print(shows)
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
            n = re.findall(" [0-9]+[.]*[0-9]* ", file)
            m = []
            for o in n:
                m.append(o.replace(" ", ""))
            print("Found episode %s in the directory." % m)
            parsed_files += m
        show_url = config["settings"]["base_url"] + "/" + show
        episodes = get_episodes(show_url)
        episodes_to_fetch = []
        for e in episodes:
            if e not in parsed_files:
                episodes_to_fetch.append(e)
                print("Going to attempt to find episode %s." %e)
        links_to_add = get_magnet_links(show_url, episodes_to_fetch)
        for link in tqdm(links_to_add):
            add_to_deluge(link, os.path.join(all_show_dir, show))


def add_to_deluge(link, save_path):
    def wait():
        wait_time = 0.5
        time.sleep(wait_time)
    config = configparser.ConfigParser()
    config.read("config.ini")
    url = config["deluge"]["url"]
    port = config["deluge"]["port"]
    username = config["deluge"]["username"]
    password = config["deluge"]["password"]
    chromedriver_path = config["settings"]["chromedriver_path"]
    driver = webdriver.Chrome(chromedriver_path)
    # driver.get(url+":"+port)
    driver.get("localhost:8112")
    wait()
    password_box = driver.find_element_by_name("password")
    password_box.click()
    wait()
    password_box.send_keys(password)
    login_button = driver.find_element_by_id("ext-gen155")
    login_button.click()
    # daemon_select = driver.find_element_by_id("ext-gen225")
    # daemon_select.click()
    # connect_button = driver.find_element_by_id("ext-gen213")
    # connect_button.click()
    wait()
    add_button = driver.find_element_by_id("ext-gen49")
    add_button.click()
    wait()
    url_button = driver.find_element_by_class_name("icon-add-url")
    url_button.click()
    url_textbox = driver.find_element_by_id("url")
    url_textbox.send_keys(link)
    add_magnet = driver.find_elements_by_class_name("x-btn-noicon")
    for button in add_magnet:
        try:
            button.click()
        except ElementNotVisibleException:
            pass
        except WebDriverException:
            pass
    while True:
        try:
            download_path = driver.find_element_by_id("ext-comp-1084")
            break
        except NoSuchElementException:
            wait()
    download_path.clear()
    download_path.send_keys(save_path)
    add_torrent = driver.find_element_by_id("ext-comp-1071")
    add_torrent.click()
    driver.close()


def get_magnet_links(show_url, episodes):
    wait_time = 0.15
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
    show_dir = os.path.join("D:\\", "Plex", "Anime", "hd_bot_example_dir")
    chromedriver_location = os.path.join(
        os.path.expanduser("~"), "PycharmProjects", "hd_bot", "chromedriver"
    )
    config["settings"] = {
        "base_url": "https://horriblesubs.info/shows/",
        "shows": "one-punch-man,goblin-slayer,tensei-shitara-slime-datta-ken",
        "show_dir": show_dir,
        "chromedriver_path": chromedriver_location,
    }
    config["deluge"] = {
        "url": "127.0.0.1",
        "port": "8112",
        "username": "admin",
        "password": "deluge",
    }
    with open("config.ini", "w") as configfile:
        config.write(configfile)


if __name__ == "__main__":
    set_config()
    sync()
