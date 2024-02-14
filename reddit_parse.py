import os, sys
from reddit_links import get_new_links, check_saved_links
from get_html_files import get_html_from_links
from reddit_comments import write_comments
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC


def get_driver():
    service = Service("/opt/homebrew/bin/chromedriver")
    options = webdriver.ChromeOptions()
    driver = webdriver.Chrome(service=service, options=options)
    return driver


def parse(subject, scroll=0, driver=None):
    if driver is None:
        driver = get_driver()
    if not os.path.exists(f"reddit_data/{subject}/"):
        os.mkdir(f"reddit_data/{subject}/")
    if not os.path.exists(f"reddit_data/{subject}/reddit_links.csv"):
        with open(
            f"reddit_data/{subject}/reddit_links.csv", "w", encoding="utf-8"
        ) as f:
            f.write("title,link,stored\n")
            f.write("0,0,y\n")
    if not os.path.exists(f"reddit_data/{subject}/reddit_comments.csv"):
        with open(
            f"reddit_data/{subject}/reddit_comments.csv", "w", encoding="utf-8"
        ) as f:
            f.write("comment,response\n")
    while True:
        if scroll > 0:
            get_new_links(subject, scroll, driver)  # update links
        elif not check_saved_links(subject):
            print("No new links")
            break
        try:
            get_html_from_links("reddit", subject, driver)  # update html
        except Exception as e:
            print(e)
            continue
    driver.quit()

    # write_comments()
    # time.sleep(60 * 60 * 24)  # Wait 24 hours


args = sys.argv

if len(args) > 1:
    subject = args[1]
    scroll = int(args[2])
else:
    subject = "history"
    scroll = 100
parse(subject, scroll)
