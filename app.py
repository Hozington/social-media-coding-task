from concurrent.futures import ThreadPoolExecutor, as_completed
from threading import local

import requests
from flask import Flask

app = Flask(__name__)

# Globals
THREAD = local()


@app.route("/")
def social_network_activity():
    json_response = get_stats()
    return json_response


def get_session():
    """
    Create a session if a session does not exist otherwise
    reuse the existing session.
    :return:
    """
    has_session = hasattr(THREAD, 'session')
    if has_session:
        return THREAD.session
    else:
        return requests.Session()


def request(url):
    """
    Send HTTP request
    :param url:
    :return:
    """
    session = get_session()
    return session.get(url)


def handle_api_response(api_response):
    """
    Handle API response. Return None when an error
    occurs while parsing the body of the response
    :param api_response:
    :return:
    """
    response = None
    try:
        response = api_response.json()
    except Exception as e:
        print(str(e))

    return response


def get_social_network_content(url):
    """
    Get social network content
    :param url:
    :return:
    """
    api_response = request(url)
    return handle_api_response(api_response)


def get_stat(url):
    """
    Get a numeric indicator of the amount of content
    posted on a social network.
    Default to zero if the content is None.
    :param url:
    :return:
    """
    content = get_social_network_content(url)
    count = 0 if content is None else len(content)
    key = url.rsplit('/', 1)[-1]
    return key, count


def get_stats():
    """
    Retrieve stats from the social medium endpoints
    :return:
    """
    urls = ["https://takehome.io/twitter", "https://takehome.io/facebook", "https://takehome.io/instagram"]
    executor = ThreadPoolExecutor()
    stats = {}
    future = {executor.submit(get_stat, url): url for url in urls}
    for i in as_completed(future):
        try:
            key, count = i.result()
            stats[key] = count
        except Exception as e:
            print(str(e))

    executor.shutdown()

    return stats
