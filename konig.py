# Copyright 2013 Kyle Maxwell

# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.

# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.

# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

# external dependencies
import ssdeep
import networkx as nx
import matplotlib.pyplot as plt

# built-in modules
import argparse
import os
import json
import pickle

def calculatehashes(directory, oldhashes={}):
    ourhashes = {}

    # get list of all files in the directory
    dirlist=os.listdir(directory)

    # iterate through each file
    for f in dirlist:
        # skip files already in hash DB
        if f in oldhashes:
            # use previously-calculated hash
            ourhashes[f] = oldhashes[f]
        else:
            # calculate hash and store
            ourhashes[f] = ssdeep.hash_from_file(os.path.join(directory,'/',f))

    return ourhashes

def creategraph(fuzzyhashes, threshold=50):
    G = nx.Graph()
    checkedhashes = set()

    # iterate over keys in fuzzyhashes
    for k in fuzzyhashes.iterkeys():
        # calculate similarity to all *remaining* hashes
        for l in fuzzyhashes.iterkeys():
            if (k != l) and l not in checkedhashes:
                sim = ssdeep.compare(fuzzyhashes[k], fuzzyhashes[l])
                # if similarity is >= threshold, add it to the graph
                if sim >= threshold:
                    G.add_edge(k, l, weight=sim)
        checkedhashes.add(k)

    return G

if __name__ == "__main__":
    # handle command-line stuff
    parser = argparse.ArgumentParser()
    parser.add_argument("-d", "--directory", help="Directory of files to be hashed", default=".")
    parser.add_argument("-t", "--threshold", help="Threshold for similarity", default=80)
    parser.add_argument("-o", "--output", help="Optional file to save fuzzy hashes")
    parser.add_argument("-i", "--input", help="Optional JSON file with existing fuzzy hashes")
    parser.add_argument("-f", "--file", help="Optional file for investigation")
    parser.add_argument("-e", "--export", help="Optional filename for exporting graph (as GraphML)")
    parser.add_argument("-l", "--load", help="Optional filename for loading graph object")
    parser.add_argument("-s", "--save", help="Optional filename for saving graph object")
    parser.add_argument("-n", "--noplot", help="Do not plot the graph using matplotlib", action="store_true")

    args = parser.parse_args()

    simthreshold = int(args.threshold)
    oldhashes = {}

    if args.input:
        print("Loading saved hash database")
        with open(args.input, 'rb') as f:
            oldhashes=json.load(f)

    # first calculate all the fuzzy hashes for the files in a directory
    # get this directory from a command-line argument
    print("Calculating fuzzy hashes for all files in %s..." % args.directory)
    malhashes = calculatehashes(args.directory, oldhashes) 

    if args.output:
        print("Saving hash database...")
        with open(args.output, 'wb') as f:
            json.dump(malhashes, f)

    if args.load:
        print("Loading saved graph object from %s" % args.load)
        with open(args.load, "rb") as loadfile:
            malgraph=pickle.load(loadfile)
    else:
        # now use these hashes to create an undirected graph of relationships
        # above a given threshold
        print("Creating graph structure for files with similarity >= %d..." % simthreshold)
        malgraph = creategraph(malhashes, simthreshold)
    
    if args.file:
        malgraph = malgraph.subgraph(nx.node_connected_component(malgraph, args.file)).copy()

    if args.export:
        nx.write_graphml(malgraph, args.export)
        print('Exported graph to %s' % args.export)

    if args.save:
        print("Saving graph object to %s" % args.save)
        with open(args.save,"wb") as savefile:
            pickle.dump(malgraph, savefile)

    print nx.info(malgraph)
    print "Graph density: ", nx.density(malgraph)

    if not args.noplot:
        # we should draw the graph at this point for visualization
        print("Preparing plot of graph structure...")
        nx.draw_spring(malgraph, with_labels=True)
        plt.show()
