import time, csv
from bs4 import BeautifulSoup
from driver import get_driver


def show_links(subject="history", titles=True, links=True):
    saved_titles = []
    saved_links = []
    with open(f"reddit_data/{subject}/reddit_links.csv", "r", encoding="utf-8") as f:
        reader = csv.reader(f)
        for row in reader:
            if titles:
                saved_titles.append(row[0])
            if links:
                saved_links.append(row[1])
    return saved_titles, saved_links


def update_scrolled(subject, to_scroll):
    with open(f"reddit_data/{subject}/reddit_links.csv", "r", encoding="utf-8") as f:
        reader = csv.reader(f)
        rows = list(reader)
        header = rows[0]
        old_scrolled = int(rows[1][1])
        scrolled = old_scrolled + to_scroll

    rows[1][1] = str(scrolled)
    # print(rows)
    # rows[1][2] = str(scrolled)
    # Write the modified data back to the file
    with open(
        f"reddit_data/{subject}/reddit_links.csv", "w", newline="", encoding="utf-8"
    ) as f:
        writer = csv.writer(f)
        writer.writerow(header)
        writer.writerows(rows[1:])


def get_scrolled(subject):
    with open(f"reddit_data/{subject}/reddit_links.csv", "r", encoding="utf-8") as f:
        reader = csv.reader(f)
        header = next(reader)
        scrolled = int(next(reader)[1])
    return scrolled


def get_links(subject, scrolled, to_scroll=100, driver=None):
    current_scroll = 0

    # Initialize a list to store links
    all_links = {"title": [], "link": []}

    # Navigate to the Reddit page
    driver.get(f"https://www.reddit.com/r/{subject}/")

    # Define a function to scroll down and load more content

    def scroll_down():
        nonlocal current_scroll
        for _ in range(
            scrolled + to_scroll
        ):  # You can adjust the number of times to scroll
            driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            time.sleep(2)  # Add a delay to allow content to load
            current_scroll += 1

    # Scroll down to load more content
    scroll_down()

    if current_scroll > scrolled:  # scrolled amount already saved
        page_source = driver.page_source
        soup = BeautifulSoup(page_source, "html.parser")

        post_links = soup.find_all("a", attrs={"slot": "full-post-link"})

        for element in post_links:
            href_value = element.get("href")
            # title = href_value.split("/")[-2]
            title = f"{href_value.split('/')[-3]}/{href_value.split('/')[-2]}"
            all_links["title"].append(title)
            all_links["link"].append(href_value)

    # Close the browser
    # driver.quit()

    # open a csv file with append, so old data will not be erased
    saved_titles = show_links(subject, titles=True, links=False)[0]

    with open(
        f"reddit_data/{subject}/reddit_links.csv", "a", newline="", encoding="utf-8"
    ) as csv_file:
        writer = csv.writer(csv_file)
        headers = ["title", "link", "stored"]
        if csv_file.tell() == 0:
            writer.writerow(headers)
            writer.writerow([scrolled, scrolled + to_scroll, scrolled + to_scroll, "y"])
        else:
            update_scrolled(subject, to_scroll)
        # The for loop
        for title, link in zip(all_links["title"], all_links["link"]):
            if title not in saved_titles:
                writer.writerow([title, link, "n"])

    # driver.quit()


def check_saved_links(subject):
    with open(f"reddit_data/{subject}/reddit_links.csv", "r", encoding="utf-8") as f:
        reader = csv.reader(f)
        header = next(reader)
        for row in reader:
            if row[2] == "n" or row[2] == "x":
                return True
    return False


def get_new_links(subject, scroll, driver=None):
    if driver is None:
        driver = get_driver()
    scrolled = get_scrolled(subject)
    get_links(subject, scrolled, scroll, driver)


# get_new_links(2)
