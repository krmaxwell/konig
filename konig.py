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

# built-in modules
import argparse
import os
import json
import pickle
import ConfigParser

# external dependencies
import ssdeep
import networkx as nx
import matplotlib.pyplot as plt

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

def main():
    # handle command-line stuff to override any config file options
    parser = argparse.ArgumentParser()
    parser.add_argument("-d", "--directory", help="Directory of files to be hashed")
    parser.add_argument("-t", "--threshold", help="Threshold for similarity")
    parser.add_argument("-o", "--output", help="Optional file to save fuzzy hashes")
    parser.add_argument("-i", "--input", help="Optional JSON file with existing fuzzy hashes")
    parser.add_argument("-f", "--file", help="Optional file for investigation")
    parser.add_argument("-e", "--export", help="Optional filename for exporting graph (as GraphML)")
    parser.add_argument("-l", "--load", help="Optional filename for loading graph object")
    parser.add_argument("-s", "--save", help="Optional filename for saving graph object")
    parser.add_argument("-n", "--noplot", help="Do not plot the graph using matplotlib", action="store_true")

    args = parser.parse_args()

    # read defaults first
    config = ConfigParser.RawConfigParser(allow_no_value=True)
    try:
        config.read('konig.cfg')
    except:
        print('Error reading configuration file, proceeding')

    # threshold for two files to be related
    if int(args.threshold):
        kthreshold = int(args.threshold)
    else:
        try:
            kthreshold = config.getint('Konig','threshold')
        except:
            kthreshold = 90
            print('Did not find threshold, using default %d', 
                  kthreshold

    # load old hashes if specified
    if args.input:
        inputfile = args.input
    elif config.get('Konig','hashdb'):
        inputfile = config.get('Konig','hashdb')
    else:
        inputfile = None
    
    oldhashes = {}
    if inputfile:
        print("Loading saved hash database")
        with open(args.input, 'rb') as f:
            oldhashes=json.load(f)

    # load graph if specified
    if args.load:
        print("Loading saved graph object from %s" % args.load)
        with open(args.load, "rb") as loadfile:
            malgraph=pickle.load(loadfile)
    else:
        # calculate all the fuzzy hashes for the files in a directory
        if args.directory:
            hashdir = args.directory
        elif config.get('Konig','hashdir'):
            hashdir = config.get('Konig','hashdir')
        else:
            hashdir = '.'
    
        print("Calculating fuzzy hashes for all files in %s..." % hashdir)
        malhashes = calculatehashes(hashdir, oldhashes) 
    
        # save new hashes if specified
        if args.output:
            print("Saving hash database...")
            with open(args.output, 'wb') as f:
                json.dump(malhashes, f)
    
        # now use these hashes to create an undirected graph of relationships
        print("Creating graph structure for files with similarity >= %d..." % kthreshold)
        malgraph = creategraph(malhashes, kthreshold)
        
    # calculate subgraph if file specified
    if args.file:
        malgraph = malgraph.subgraph(nx.node_connected_component(malgraph, args.file)).copy()

    # export graph to file if specified
    if args.export:
        nx.write_graphml(malgraph, args.export)
        print('Exported graph to %s' % args.export)

    # save graph to file if specified
    if args.save:
        print("Saving graph object to %s" % args.save)
        with open(args.save,"wb") as savefile:
            pickle.dump(malgraph, savefile)

    # Basic data about the graph
    print nx.info(malgraph)
    print "Graph density: ", nx.density(malgraph)

    if not args.noplot:
        # we should draw the graph at this point for visualization
        print("Preparing plot of graph structure...")
        nx.draw_spring(malgraph, with_labels=True)
        plt.show()

if __name__ == "__main__":
    main()
