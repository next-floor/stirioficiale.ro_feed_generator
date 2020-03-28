import atexit
import os
import time

import dateutil.parser
import requests
from apscheduler.schedulers.background import BackgroundScheduler
from bs4 import BeautifulSoup
from fake_useragent import UserAgent
from feedgen.feed import FeedGenerator
from flask import Flask, send_file

INTERVAL = 10
PAGE_NUM = 3
SLEEP_TIME = 3
HEADER_OBJ = {
    'User-Agent': str(UserAgent().random)
}

os.chdir(os.path.dirname(os.path.abspath(__file__)))


class Item:
    def __init__(self, title, author, body, date, update, guid):
        self.title = title
        self.author = author
        self.body = body
        self.date = date
        self.update = update
        self.guid = guid

        if not self.update:
            self.update = date

    def handle_entry(self, entry):
        entry.title(self.title)
        entry.author(name=self.author)
        entry.description(self.body)
        entry.pubDate(self.date)
        entry.updated(self.update)
        entry.link(href=self.guid)
        entry.guid(self.guid)


def scrape_page(page_num):
    link_str = 'https://stirioficiale.ro/informatii?page={}'.format(page_num)
    resp = requests.get(link_str, headers=HEADER_OBJ, timeout=15)

    if resp.status_code != 200:
        return

    time.sleep(SLEEP_TIME)  # be nice and don't hammer the site

    soup = BeautifulSoup(resp.content, 'html.parser')

    ret_arr = []

    for article in soup.find_all('article'):
        article_body = article.div
        divs = article_body.find_all('div')

        title = ' '.join(article_body.h1.text.split())
        author = ' '.join(divs[0].text.split()[4:])
        article_text = ' '.join(divs[-2].text.split())
        date = dateutil.parser.parse(divs[0].time['datetime'])
        update = None
        link_guid = divs[-1].a['href']

        if len(divs) == 6 and 'actualizat' in divs[3].text.lower():
            update = dateutil.parser.parse(divs[3].time['datetime'])

        ret_arr.append(Item(title, author, article_text, date, update, link_guid))

    return ret_arr


def generate_xml():
    arr = []

    for ind in range(PAGE_NUM, 0, -1):
        arr += scrape_page(ind)

    arr.sort(key=lambda x: x.update)

    feeder = FeedGenerator()

    feeder.language('ro')
    feeder.title('stirioficiale.ro')
    feeder.id('https://stirioficiale.ro/informatii')
    feeder.link(href='https://stirioficiale.ro/informatii', rel='alternate')
    feeder.description('Informații din surse sigure')
    feeder.ttl(INTERVAL * 60)
    feeder.updated(arr[-1].update)

    for elem in arr:
        entry = feeder.add_entry()
        elem.handle_entry(entry)

    feeder.rss_file('rss.xml', pretty=True)
    feeder.atom_file('atom.xml', pretty=True)


scheduler = BackgroundScheduler()
scheduler.add_job(func=generate_xml, trigger='interval', seconds=60 * (INTERVAL - 1))
scheduler.start()

app = Flask(__name__)


@app.route('/favicon.ico')
def favicon_route():
    return send_file('favicon.ico')


@app.route('/feed/rss')
def rss_route():
    return send_file('rss.xml')


@app.route('/feed/atom')
def atom_route():
    return send_file('atom.xml')


atexit.register(lambda: scheduler.shutdown())

if __name__ == '__main__':
    generate_xml()
    app.run(host='0.0.0.0', port=5000, threaded=True)
