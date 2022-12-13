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
    Send HTTP GET request
    :param url:
    :return:
    """
    session = get_session()
    return session.get(url)


def get_api_response_body(api_response):
    """
    Handle API response. Return None when an error
    occurs while parsing the body of the response
    or a 200 response is not received
    :param api_response:
    :return:
    """
    body = None

    if api_response.status_code != 200:
        return body

    try:
        body = api_response.json()
    except Exception as e:
        print(str(e))

    return body


def get_stat(config):
    """
    Get a numeric indicator of the amount of content
    posted on a social network.
    Default to zero if the content is None.
    :param config:
    :return:
    """
    url = config.get("url")
    api_response = request(url)
    content = get_api_response_body(api_response)

    count = 0 if content is None else len(content)
    key = config.get("identifier")
    return key, count


def get_stats():
    """
    Retrieve stats from the social medium endpoints
    :return:
    """
    config = [
        {"url": "https://takehome.io/twitter", "identifier": "twitter"},
        {"url": "https://takehome.io/facebook", "identifier": "facebook"},
        {"url": "https://takehome.io/instagram", "identifier": "instagram"}
    ]
    executor = ThreadPoolExecutor()
    stats = {}
    future = {executor.submit(get_stat, config_item): config_item for config_item in config}
    for i in as_completed(future):
        try:
            key, count = i.result()
            stats[key] = count
        except Exception as e:
            print(str(e))

    executor.shutdown()

    return stats
