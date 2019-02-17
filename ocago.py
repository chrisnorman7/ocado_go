"""Get the cheapest price from Ocado."""

from argparse import ArgumentParser
from json import loads, dump
from urllib.parse import quote
from bs4 import BeautifulSoup
from requests import Session

pound = chr(163)
http = Session()

base_url = 'https://www.ocado.com/search?entry='

parser = ArgumentParser()

parser.add_argument(
    '-v', '--verbose', action='store_true', default=False,
    help='Verbose output'
)

parser.add_argument('thing', nargs='+', help='Thing to search for')


def main():

    def vprint(*a, **kw):
        """Verbose printing."""
        if args.verbose:
            return print(*a, **kw)

    args = parser.parse_args()
    entry = ' '.join(args.thing)
    url = base_url + quote(entry)
    vprint('Fetching URL %s...' % url)
    res = http.get(url)
    if not res.ok:
        return vprint('Error: %r.' % res)
    vprint('Parsing HTML...')
    s = BeautifulSoup(res.content, 'html.parser')
    vprint('Extracting JSON blob...')
    data = s.body.find('script').text.strip().split(' = ')[1].strip(';')
    vprint('Loading JSON...')
    data = loads(data)
    vprint('Fetching products...')
    products = data['products']['productsBySku']
    if not products:
        return print('No products found.')
    cheapest_product = {}
    cheapest_price = {}
    for product in products.values():
        price = product['price']
        if 'unit' not in price:
            continue
        try:
            price = price['unit']
            current = price.get('price', price.get('current', None))
        except KeyError:
            with open('product.json', 'w') as f:
                dump(product, f, indent=4)
            raise
        if 'per' not in price:
            continue
        per = price['per']
        price = price['price']
        if per == 'per 100ml':
            per = 'per litre'
            price *= 10
        elif per == 'per 100g':
            per = 'per kg'
            price *= 10
        elif per == 'per 1g':
            per = 'per kg'
            price *= 1000
        if per not in cheapest_product:
            cheapest_product[per] = product
        if per not in cheapest_price:
            cheapest_price[per] = price
        vprint(product['name'])
        vprint('%s%.2f per %s.' % (pound, price, per))
        if price < cheapest_price[per]:
            cheapest_price[per] = price
            cheapest_product[per] = product
    for per, product in cheapest_product.items():
        name = product['name']
        sku = product['sku']
        current = product['price']['current']
        price = cheapest_price[per]
        print('%s: %s (#%s).' % (per.capitalize(), name, sku))
        print('%s%.2f (%s%.2f %s).' % (pound, current, pound, price, per))


if __name__ == '__main__':
    main()
