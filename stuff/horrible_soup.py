from bs4 import BeautifulSoup
import requests


def get_show_list():
    wp = requests.get(url='https://horriblesubs.info/shows/')
    soup = BeautifulSoup(wp.text, features="html5lib")
    soup = soup.find_all('div', attrs={'class': ['ind-show']})
    return[item.text for item in soup]


def get_eps(show: str):
    show = show.lower()
    show = show.replace(" ", '-')
    wp = requests.get(url='https://horriblesubs.info/shows/%s/' % show)
    soup = BeautifulSoup(wp.text, features="html5lib")
    print(soup.prettify())


if __name__ == "__main__":
    shows = get_show_list()
    for show in shows:
        get_eps(show)
