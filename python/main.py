#!/usr/bin/env python
# encoding: utf-8

import json
import re
import pprint
import collections

def Tree(): return collections.defaultdict(Tree)

listings_data = []
products_data = []

prod_tree = Tree()

with open('./data/listings.txt') as listings_file:
    for line in listings_file:
        listings_data.append(json.loads(line))

with open('./data/products.txt') as products_file:
    for line in products_file:
        product = json.loads(line)
        product['listings'] = list()
        products_data.append(product)

        product_tokens = product['product_name'].lower().replace('_', '-').split('-')
        tree = prod_tree
        while len(product_tokens) > 1:
            tree = tree[product_tokens.pop(0)]

        tree[product_tokens.pop(0)] = product

def match_listing(tokens, tree, mlist):
    if 'model' in tree:
        mlist.append(tree)
    else:
        matches = set(tokens).intersection(tree)
        for match in matches:
            match_listing(tokens, tree[match], mlist)

match_count = 0
close_match = 0
    
for listing in listings_data:
    delimiters = " ", ",", "_", "-", "[", "]", "/", "+", ";", "®"
    regexPattern = '|'.join(map(re.escape, delimiters))
    listing_tokens = re.split(regexPattern, listing['title'].lower())

    mlist = list()
    match_listing(listing_tokens, prod_tree, mlist)
    level = 0

    if len(mlist) > 1: #i.e. multiple matches probably means dubious matchs
        close_match += 1
    elif len(mlist) > 0:
        for product in mlist:
            product['listings'].append(listing)
            match_count += 1


with open('results.txt', 'w') as fp:
    for product in products_data:
        result = {'product_name':product['product_name'], 'listings':product['listings']}
        json.dump(result, fp)
        fp.write('\n')

print('Match count: ' + str(match_count))
print('Reject count: ' + str(len(listings_data) - match_count))
                    
