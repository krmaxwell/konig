import ssdeep
import networkx as nx
import argparse

def calculatehashes()
def creategraph()

def main():

if __name__ == "__main__":
    # first calculate all the fuzzy hashes for the files in a directory
    # get this directory from a command-line argument
    malhashes = calculatehashes(dir) 

    # now use these hashes to create an undirected graph of relationships
    # above a given threshold
    malgraph = creategraph(malhashes, threshold=80)

    # we should draw the graph at this point for visualization
    drawgraph(malgraph)
