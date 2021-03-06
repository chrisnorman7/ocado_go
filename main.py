"""Ocado Go server."""

import logging
from argparse import ArgumentParser, ArgumentDefaultsHelpFormatter
from json import loads
from urllib.parse import quote
from bs4 import BeautifulSoup

from flask import Flask, jsonify, render_template, request
from gevent import get_hub
from gevent.pool import Pool
from gevent.pywsgi import WSGIServer
from requests import Session

http = Session()
ocado_url = 'https://www.ocado.com'
search_url = ocado_url + '/search?entry='
app = Flask(__name__)

parser = ArgumentParser(formatter_class=ArgumentDefaultsHelpFormatter)

parser.add_argument(
    '-i', '--interface', default='0.0.0.0', help='The interface to bind to'
)

parser.add_argument(
    '-p', '--port', type=int, default=6223, help='The port to listen on'
)

parser.add_argument(
    '-d', '--debug', action='store_true', default=False,
    help='Enable debugging mode'
)


def error(msg):
    """Return an error dictionary."""
    return {'error': msg}


def search(string):
    """Perform a search and return a dictionary of results. If an error occurs,
    a dictionary with a single key "error" will be returned."""
    try:
        results_url = search_url + quote(string)
        res = http.get(results_url)
        if not res.ok:
            return error('Error: %r.' % res)
        s = BeautifulSoup(res.content, 'html.parser')
        data = s.body.find('script').text.strip().split(' = ')[1].strip(';')
        data = loads(data)
        products_data = data['products']['productsBySku']
        products = {}
        for product in products_data.values():
            price = product['price']
            try:
                current = price['current']
            except KeyError:
                current = price['unit']['price']
            if 'unit' not in price:
                price['unit'] = dict(per='each', price=current)
            price = price['unit']
            per = price.get('per', 'each')
            price = price['price']
            if per == 'per 10ml':
                per = 'per litre'
                price *= 100
            elif per == 'per 100ml':
                per = 'per litre'
                price *= 10
            elif per == 'per 100g':
                per = 'per kg'
                price *= 10
            elif per == 'per 1g':
                per = 'per kg'
                price *= 1000
            elif per == 'per 10g':
                per = 'per kg'
                price *= 100
            else:
                price = current
            if per not in products:
                products[per] = []
            sku = product['sku']
            app_url = search_url + sku
            name = product['name']
            weight = product.get('catchWeight', '')
            images = s.find_all('img', {'alt': name})
            if len(images) == 1:
                img = images[0]
            else:
                for img in images:
                    parent = img.parent.parent.parent
                    span = parent.find(
                        'span', {'class': 'fop-catch-weight'}
                    )
                    if span is not None and span.text == weight:
                        break
            image_url = ocado_url + img.get('src')
            url = img.parent.parent.parent.parent
            url = url.get('href')
            url = ocado_url + url
            products[per].append(
                dict(
                    sku=sku, name=name, price=current, per=price, url=url,
                    weight=weight, image=image_url, app_url=app_url
                )
            )
        if not products:
            return error('No products to show.')
        for per, data in products.copy().items():
            products[per] = sorted(data, key=lambda thing: thing['per'])
        return dict(search_url=results_url, products=products)
    except Exception:
        logging.exception('Search string %r caused an error.', string)
        return error('Your search caused an error which has been reported.')


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/ocado/', methods=['GET', 'POST'])
def ocado_search():
    string = request.form['string']
    results = search(string)
    return jsonify(results)


if __name__ == '__main__':
    logging.basicConfig(filename='errors.log', level='INFO')
    args = parser.parse_args()
    get_hub().NOT_ERROR += (KeyboardInterrupt,)
    http_server = WSGIServer((args.interface, args.port), app, spawn=Pool())
    try:
        http_server.serve_forever()
    except KeyboardInterrupt:
        pass
