import os
import argparse
import xml.etree.ElementTree as ET
import pandas as pd
import numpy as np
import csv
import re
import pprint

# Useful if you want to perform stemming.
import nltk
stemmer = nltk.stem.PorterStemmer()

categories_file_name = r'/workspace/datasets/product_data/categories/categories_0001_abcat0010000_to_pcmcat99300050000.xml'

queries_file_name = r'/workspace/datasets/train.csv'
output_file_name = r'/workspace/datasets/fasttext/labeled_queries.txt'

parser = argparse.ArgumentParser(description='Process arguments.')
general = parser.add_argument_group("general")
general.add_argument("--min_queries", default=1,  help="The minimum number of queries per category label (default is 1)")
general.add_argument("--output", default=output_file_name, help="the file to output to")

args = parser.parse_args()
output_file_name = args.output

if args.min_queries:
    min_queries = int(args.min_queries)

# The root category, named Best Buy with id cat00000, doesn't have a parent.
root_category_id = 'cat00000'

tree = ET.parse(categories_file_name)
root = tree.getroot()

# Parse the category XML file to map each category id to its parent category id in a dataframe.
categories = []
parents = []
for child in root:
    id = child.find('id').text
    cat_path = child.find('path')
    cat_path_ids = [cat.find('id').text for cat in cat_path]
    leaf_id = cat_path_ids[-1]
    if leaf_id != root_category_id:
        categories.append(leaf_id)
        parents.append(cat_path_ids[-2])
parents_df = pd.DataFrame(list(zip(categories, parents)), columns =['category', 'parent'])

# Read the training data into pandas, only keeping queries with non-root categories in our category tree.
queries_df = pd.read_csv(queries_file_name)[['category', 'query']]
queries_df = queries_df[queries_df['category'].isin(categories)]

# Convert queries to lowercase, and optionally implement other normalization, like stemming.
NONALPHA_RE = re.compile('[^a-zA-Z0-9]+')
def _convertquery(query):
    q = query.lower()
    q = NONALPHA_RE.sub(' ', q)
    tokens = q.split()
    return ' '.join([stemmer.stem(t) for t in tokens])
queries_df["query"] = queries_df["query"].apply(_convertquery)

category_count_series = queries_df.groupby("category").size()
print("initial number of categories with queries: {}".format(len(category_count_series)))

# Roll up categories to ancestors to satisfy the minimum number of queries per category.

print("rolling")
updatecount=0
visited =0
MAX_UPDATE = None # for debugging/testing
def _handle_node(nodes):
    global updatecount
    global queries_df
    global MAX_UPDATE
    global visited
    visited+=1
    node=nodes[-1]
    children = tuple(parents_df[parents_df["parent"]==node]["category"].values)
    if not children:
        return
    if MAX_UPDATE and (updatecount>=MAX_UPDATE):
        return
    #print("_handle_node: {} , children={}".format(nodes, children))

    # first, let children do their roll-ups
    for child in children:
        _handle_node(nodes+[child])
        if MAX_UPDATE and (updatecount>=MAX_UPDATE):
            return

    # second, do my roll-ups, if needed
    if node==root_category_id:
        return
    for child in children:
        child_queries_df = queries_df[queries_df["category"]==child]
        print("visited={}: category {} has queries: {}".format(visited, nodes+[child], len(child_queries_df)))
        if (len(child_queries_df)==0) or len(child_queries_df) >= min_queries:
            continue
        # roll up to me
        print("ROLLING updatecount={}, parent={}, child={} count={!r}".format(updatecount, node, child, len(child_queries_df)))
        update_indexes = []
        update_categories = []
        update_queries = []
        for index, cols in child_queries_df.iterrows():
            update_indexes.append(index)
            update_categories.append(node)
            update_queries.append(cols["query"])
        queries_df.update(pd.DataFrame({"category":update_categories, "query":update_queries}, index=update_indexes))
        updatecount+=1
        if MAX_UPDATE and (updatecount>=MAX_UPDATE):
            return

_handle_node([root_category_id])
print("done rolling")

print("post-roll queries_df rows: {}".format(len(queries_df)))
category_count_series = queries_df.groupby("category").size()
print("post-roll number of categories with queries: {}".format(len(category_count_series)))

# Create labels in fastText format.
queries_df['label'] = '__label__' + queries_df['category']

# Output labeled query data as a space-separated file, making sure that every category is in the taxonomy.
queries_df = queries_df[queries_df['category'].isin(categories)]
queries_df['output'] = queries_df['label'] + ' ' + queries_df['query']
queries_df[['output']].to_csv(output_file_name, header=False, sep='|', escapechar='\\', quoting=csv.QUOTE_NONE, index=False)
