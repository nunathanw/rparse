import requests, csv, time, re, os
from reddit_comments import write_comments
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

main_comments_button_class = """
button-small px-[length:var(--rem10)]
button-brand



button inline-flex items-center justify-center """

other_comments_button_class = "text-tone-2 text-12 no-underline hover:underline px-xs py-xs flex ml-[3px] xs:ml-0 !bg-transparent !border-0"


def get_driver():
    service = Service("/opt/homebrew/bin/chromedriver")
    options = webdriver.ChromeOptions()
    driver = webdriver.Chrome(service=service, options=options)
    return driver


def get_html(url, driver):
    time.sleep(1)
    driver.get(url)
    time.sleep(1)
    other_comments_errors = 0
    main_comments_errors = 0
    no_more_buttons = 0
    button_click_errors = {}
    while (
        other_comments_errors <= 3
        and main_comments_errors <= 3
        and no_more_buttons <= 3
    ):
        try:
            other_comments_buttons = driver.find_elements(
                By.XPATH,
                f"//div[@class='inline-block ml-px']//button[contains(@class, '{other_comments_button_class}')]//span[contains(text(), 'more repl')]",
            )

        except Exception as e:
            print("Button or following element not found")
            other_comments_errors += 1
            other_comments_buttons = []

        other_comments_buttons = list(
            filter(
                lambda b: button_click_errors.get(str(b), 0) < 3,
                other_comments_buttons,
            )
        )

        for button in other_comments_buttons:
            # time.sleep(0.5)
            try:
                # Wait for the button to become clickable
                WebDriverWait(driver, 10).until(
                    EC.element_to_be_clickable(
                        (
                            By.XPATH,
                            f"//button[contains(@class, '{other_comments_button_class}')]",
                        )
                    )
                )

                button.click()
                time.sleep(0.5)
            except Exception as e:
                print(f"error clicking button: {e}")
                if str(button) not in button_click_errors:
                    button_click_errors[str(button)] = 0
                button_click_errors[str(button)] += 1
                if button_click_errors[str(button)] >= 5:
                    other_comments_buttons.remove(button)
                print(button_click_errors)

        try:
            main_comments_button = driver.find_elements(
                By.XPATH,
                f"//div[@class='inline-block mt-[2px] ml-px']//button[contains(@class, '{main_comments_button_class}')]",
            )
            for button in main_comments_button:
                button.click()
                time.sleep(0.5)

        except Exception as e:
            print("Button or following element not found")
            main_comments_errors += 1

        if len(other_comments_buttons) == 0:
            no_more_buttons += 1
            print("No more buttons found", no_more_buttons)
            driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            time.sleep(2)

    driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")

    html = driver.page_source
    return html


def get_html_from_links(site="reddit", subject="Literature", driver=None):
    if driver is None:
        driver = get_driver()

    with open(f"reddit_data/{subject}/reddit_links.csv", "r", newline="") as file:
        reader = csv.reader(file)
        rows = list(reader)

    for row in rows[2:]:
        if len(row) != 3:
            continue
        else:
            if row[2] != "n":
                continue
        url = f"https://www.reddit.com{row[1]}"

        # scroll_down()
        html = get_html(url, driver)
        soup = BeautifulSoup(html, "html.parser")

        html_str = str(soup)

        # with open(f"{site}_html/{row[0]}.html", "w", encoding="utf-8") as f:
        #     f.write(html_str)

        try:
            write_comments(subject, html_str, url)
        except Exception as e:
            print(e)
            if len(row) >= 3:
                row[2] = "x"
            with open(
                f"reddit_data/{subject}/reddit_links.csv", "w", newline=""
            ) as file:
                writer = csv.writer(file)
                writer.writerows(rows)
            continue

        time.sleep(3)

        if len(row) >= 3:
            row[2] = "y"

        with open(f"reddit_data/{subject}/reddit_links.csv", "w", newline="") as file:
            writer = csv.writer(file)
            writer.writerows(rows)
