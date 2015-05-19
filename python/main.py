#!/usr/bin/env python
# encoding: utf-8

import json, re, collections, codecs

def Tree(): return collections.defaultdict(Tree)

def search(tokens, tree, mlist):
    if 'model' in tree: #i.e. a leaf in the tree
        mlist.append(tree)
    else:
        matches = set(tokens).intersection(tree)
        for match in matches:
            search(tokens, tree[match], mlist)

def main():

    products = []
    prod_tree = Tree()
            
    for line in codecs.open("./data/products.txt", encoding="UTF-8").readlines():
        product = json.loads(line)
        product['listings'] = list()
        product_tokens = product['product_name'].lower().replace('_', '-').split('-')

        tree = prod_tree        
        while len(product_tokens) > 1:
            tree = tree[product_tokens.pop(0)]
        tree[product_tokens.pop(0)] = product
        
        products.append(product)

    match_count = 0
    total_listings = 0

    for line in codecs.open("./data/listings.txt", encoding="UTF-8").readlines():
        listing = json.loads(line)
        delimiters = " ", ",", "_", "-", "[", "]", "/", "+", ";", "®"
        regex_pattern = '|'.join(map(re.escape, delimiters))
        listing_tokens = re.split(regex_pattern, listing['title'].lower())
        
        mlist = list()
        search(listing_tokens, prod_tree, mlist)
        total_listings += 1
        
         # multiple (complete) matches probably means dubious matches, so allow only one
        if len(mlist) == 1:
            for product in mlist:
                product['listings'].append(listing)
                match_count += 1

    with open('results.txt', 'w') as fp:
        for product in products:
            result = {'product_name':product['product_name'], 'listings':product['listings']}
            json.dump(result, fp)
            fp.write('\n')

    print('Match count: ' + str(match_count))
    print('Reject count: ' + str(total_listings - match_count))

main()
                    
