# To run:
## Python Solution

```sh
cd ./python
./challenge.py
```

## C++ Solution
(note, a c++11-enabled compiler must be used)
```sh
# Install necessary libraries
apt-get install libjsoncpp-dev libboost-dev

# make and run
cd ./cpp && make && ./challenge
```

# Some Commentary

## Observations about the sample data

A few observations about the sample data lead to certain
algorithmic strategies:

* There are few if any errors in a given listing's model
  id/string. Even if there were, it would be bad to try to match them,
  e.g. "Sony Cyber-shot DSC-HX5" with "Sony Cyber-shot
  DSC-WX5". Therefore no fuzzy string scoring (in the traditional
  sense of Levenshtein or Jaro-Winkler) should be attempted with the
  model string. 
* Model strings are inconsistent in their use of various delimiters,
  e.g. spaces, dashes, and periods. To illustrate, DSCS2100 should
  probably match DSC-S2100.
* Listings inconsistently include the product 'family' in the model
  string, especially among European listings e.g. "Sony Alpha
  DSLR-A230" vs. "Sony - DSLR-A230".
* In general, things are case-insensitive (e.g Canon === CANON)

Exact string matching is therefore employed in both solutions, using a
"parse-tree" to speed up matching slightly.

Other categorization methods involve classifying each listing by
its supplementary data such as the matched product's 'announced-date'
and 'price'. One strategy might involve scoring the price of each
listing according to how far away from the mean price for that
product, basically rejecting bizarre pricing. This is not done in
either solution for the sake of simplicity.

### What delimits a token?
In general, the characters '._-,' are all considered as delimiters,
and '[]/+;®' are considered junk characters. This means a title of
'Sony - DSLR+A-230' will be overlooked. This is totally arbitrary, and
it is hard to judge what non-alphanumeric characters should represent.

## Python Solution

A tree of tokens is created first, parsed from each
'product_name'. Then, each listing's 'name' field is parsed, and the
tree is searched for a match. If there is a unique match, the match is
deemed a success.

A illustration of the tree structure:
```
Tree Depth (d) ->

   d=0      d=1        d=2        d=3       d=4
 ------   -------   ---------    -----    -------

                 /  ALPHA     -  DSLR   - A230 
          SONY -
       /         \  TX10
(root)<
       \                       / A5     - Zoom        
          CANON  -  POWERSHOT - 
                               \ SD980  - IS
```


The drawback to naively parsing the 'product_name' is that for
listings to match, they must contain *all* the tokens seen in the
'product_name'. This is problematic for listings missing the product
family string. The example given above illustrates this: "Sony -
DSLR-A230" will not match "Sony Alpha DSLR-A230" because the path in
the tree that implies a match (SONY -> ALPHA -> DSLR -> A230) will not
be found when the listing's 'name' doesn't contain the string
'Alpha'. 

## C++ Solution

A very similar strategy to the Python solution is used. To combat the
missing family string problem from the python solution, a slight
modification is made. The tree is formed with two levels - one for
for the manufacturer, and one for the product name. The tradeoff is
that search times increase, since there are more nodes at a given tree
depth.

Also used is a one-token 'look ahead' to match listings who's
'product_name' has been erroneously tokenized (or at least tokenized
rather aggressively). For example, 'Sony Alpha NEX 5' should match to
the 'Sony NEX-5', but the tree path that should be followed looks like
(SONY->NEX5) due to delimiter elimination. When 'NEX' and '5' are
concatenated, it will correctly match the 'NEX5' tree node.
