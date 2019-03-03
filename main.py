"""Ocado Go server."""

from argparse import ArgumentParser, ArgumentDefaultsHelpFormatter
from json import loads
from urllib.parse import quote
from bs4 import BeautifulSoup
from flask import Flask, jsonify, render_template, request
from gevent.pywsgi import WSGIServer
from requests import Session

http = Session()
base_url = 'https://www.ocado.com/search?entry='
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
    url = base_url + string
    res = http.get(url)
    if not res.ok:
        return error('Error: %r.' % res)
    s = BeautifulSoup(res.content, 'html.parser')
    data = s.body.find('script').text.strip().split(' = ')[1].strip(';')
    data = loads(data)
    products_data = data['products']['productsBySku']
    products = {}
    for product in products_data.values():
        price = product['price']
        current = price['current']
        if 'unit' not in price:
            price['unit'] = dict(per='each', price=current)
        price = price['unit']
        per = price.get('per', 'each')
        price = price['price']
        if per == 'per 10ml':
            per = 'per litre'
            price *= 100
        if per == 'per 100ml':
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
        if per not in products:
            products[per] = []
        sku = product['sku']
        products[per].append(
            dict(
                sku=sku, name=product['name'],
                price=current, per=price, url=base_url + sku,
                weight=product.get('catchWeight', '')
            )
        )
    if not products:
        return error('No products to show.')
    for per, data in products.copy().items():
        products[per] = sorted(data, key=lambda thing: thing['per'])
    return products


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/ocado/', methods=['GET', 'POST'])
def ocado_search():
    string = request.form['string']
    string = quote(string)
    results = search(string)
    return jsonify(results)


if __name__ == '__main__':
    args = parser.parse_args()
    http_server = WSGIServer((args.interface, args.port), app)
    try:
        http_server.serve_forever()
    except KeyboardInterrupt:
        pass
