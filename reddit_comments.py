import requests, re, csv
from bs4 import BeautifulSoup


# def
def get_html(url):
    response = requests.get(url)
    return response.text


def get_text(element):
    current_response = element.find("div", id="-post-rtjson-content").get_text(
        # strip=True
    )
    return current_response


def recursive_comments(comment_element, comment, comments_dict={}):
    current_response = comment_element.find("div", id="-post-rtjson-content").get_text()
    current_response = re.sub("\n+", "\n", current_response)
    current_response = re.sub(r"\s+", " ", current_response)

    votes = comment_element.attrs.get("score", 0)
    username = comment_element.attrs.get("author", "NA")

    # current_response = f"{votes}_{current_response}"

    get_responses = comment_element.find("div", slot="children")

    if get_responses:
        responses = get_responses.find_all("shreddit-comment", recursive=False)
    else:
        responses = []

    if comment not in comments_dict:
        comments_dict[comment] = [f"[{votes}&&{username}&&{current_response}]"]
    else:
        comments_dict[comment].append(f"[{votes}&&{username}&&{current_response}]")

    for response in responses:
        recursive_comments(response, current_response, comments_dict)
    return comments_dict


def get_comments(html, url):
    soup = BeautifulSoup(html, "html.parser")
    post_container = soup.find("shreddit-post")
    # votes = post_container.attrs["score"] if post_container.attrs.get("score") else 0
    # get username
    username = post_container.attrs.get("author", "NA")
    votes = post_container.attrs.get("score", 0)
    title = post_container.attrs.get("post-title", url)
    # print(username, title, votes)
    # print(post_container.attrs)
    # title = (
    #     post_container.find("div", slot="title").get_text(
    #         # strip=True
    #     )
    #     if post_container
    #     else ""
    # )
    title = f"[{votes}&&{username}&&POST={title}]"
    post_text = post_container.find("div", slot="text-body")
    if post_text:
        post_contents = title + "\n".join(
            paragraph.get_text(
                # strip=True
            )
            for paragraph in post_text.find_all("p")
        )
    else:
        post_contents = title
    comments_dict = {post_contents: []}
    comment_tree = soup.find("shreddit-comment-tree", id="comment-tree")
    if comment_tree:
        comments = comment_tree.find_all("shreddit-comment", recursive=False)
        for comment in comments:
            recursive_comments(comment, post_contents, comments_dict)
        # recursive_comments(comment_tree, body, comments_dict)

    return comments_dict


def write_comments(subject, html, url):
    comments = get_comments(html, url)

    with open(
        f"reddit_data/{subject}/reddit_comments.csv", "a", newline="", encoding="utf-8"
    ) as csvfile:
        csv_writer = csv.writer(csvfile)

        # Check if the file is empty, and if so, write the header
        if csvfile.tell() == 0:
            csv_writer.writerow(["comment", "response"])

        # Loop through the comments and responses
        for comment, responses in comments.items():
            # Clean the comment
            if comment is None:
                comment = f"NA {url}"
            comment = comment.rstrip()
            comment = re.sub(r"\s+", " ", comment).strip()
            comment = re.sub(r"\n+", " ", comment).strip()
            comment = re.sub(r"\t+", " ", comment).strip()

            # Loop through responses and clean each response
            for response in responses:
                if response is None:
                    response = f"NA {url}"
                response = response.rstrip()
                response = re.sub(r"\s+", " ", response).strip()
                response = re.sub(r"\n+", " ", response).strip()
                response = re.sub(r"\t+", " ", response).strip()

                # Write the comment and response to the CSV file
                csv_writer.writerow([comment, response])


# html = open(
#     "reddit_html/does_succor_and_sucker_sound_different.html",
#     "r",
#     encoding="utf-8",
# ).read()

# comments = get_comments(html)

# with open("extract.html", "r", encoding="utf-8") as f:
#     no_extract = f.read()
#     comments = get_comments(no_extract, "url")
#     for comment in comments:
#         for response in comments[comment]:
#             print(f"{comment}\t\t{response}")
#             print()


# for comment, responses in comments.items():
#     for response in responses:
#         print(comment, " : ", response.strip())
#         print()
