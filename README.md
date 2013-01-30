konig
=====

Graph-theoretical investigation of a corpus of malware obtained from the web using [mwcrawler](https://github.com/technoskald/mwcrawler). Named for [Dénes Kőnig](http://en.wikipedia.org/wiki/D%C3%A9nes_K%C5%91nig), who wrote the first textbook on graph theory.

Usage
-----
    python konig.py [OPTIONS]

    OPTION LIST:

    -d    Directory of files to be hashed. Defaults to current directory if not specified.
    -t    Threshold of similarity before files are considered linked, on 0-100 scale. Defaults to 80 if not specified.
    -o    Output file for fuzzy hashes once calculated. Stored in JSON format.
    -i    Input file for previously-calculated fuzzy hashes. Must be in JSON format (e.g. created with -o above). Note that any files listed here will NOT be rehashed, even if they have changed.
    -f    Investigation file. Konig will calculate the graph, then present the connected component graph containing this file (everything related to it, directly or indirectly).
    -e    Export file. Save your graph as GraphML for use in other tools.
    -n    Do not plot (interactively). GraphML export is not affected by this switch.

Note that once the graph displays, you can click on the Zoom-to-rectangle button to select an area for closer examination. See the [matplotlib docs](http://matplotlib.org/users/navigation_toolbar.html) for more information. Alternately, you can import the GraphML file into [Gephi](https://gephi.org) or similar.

Requirements
------------
* [ssdeep](http://pypi.python.org/pypi/ssdeep)
* [NetworkX](http://networkx.github.com)
* [matplotlib](http://matplotlib.org/)

Copyright 2013, Kyle Maxwell. Licensed under GPL v3. See LICENSE for more details.
