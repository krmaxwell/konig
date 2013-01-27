import ssdeep
import networkx as nx
import matplotlib.pyplot as plt

import argparse
import os

def calculatehashes(directory):
    ourhashes = {}

    # get list of all files in the directory
    dirlist=os.listdir(directory)

    # iterate through each file
    for f in dirlist:
        # calculate hash and store
        ourhashes[f] = ssdeep.hash_from_file(directory+'/'+f)

    return ourhashes

def creategraph(fuzzyhashes, threshold=50):
    G = nx.Graph()

    # iterate over keys in fuzzyhashes
    for k in fuzzyhashes.iterkeys():
        # calculate similarity to all *remaining* hashes
        # TODO: fix this so we don't repeat ourselves, this is way naive
        for l in fuzzyhashes.iterkeys():
            if (k != l):        # literally the ONLY optimization so far
                sim = ssdeep.compare(fuzzyhashes[k], fuzzyhashes[l])
                # if similarity is >= threshold, add it to the graph
                if sim >= threshold:
                    G.add_edge(k, l, weight=sim)

    return G

if __name__ == "__main__":
    # handle command-line stuff
    parser = argparse.ArgumentParser()
    parser.add_argument("-d", "--directory", help="Directory of files to be hashed", default=".")
    # TODO: use this 
    parser.add_argument("-t", "--threshold", help="Threshold for similarity", default=80)
    args = parser.parse_args()

    # first calculate all the fuzzy hashes for the files in a directory
    # get this directory from a command-line argument
    print("Calculating fuzzy hashes for all files in %s..." % args.directory)
    malhashes = calculatehashes(args.directory) 

    # now use these hashes to create an undirected graph of relationships
    # above a given threshold
    print("Creating graph structure for files with similarity >= 80...")
    malgraph = creategraph(malhashes, threshold=80)

    # we should draw the graph at this point for visualization
    print("Preparing plot of graph structure...")
    nx.draw_spring(malgraph, with_labels=False)
    plt.show()
