import re
import sys


regexs = ["^\(", "^\w", "\W$"]
ExpandedQueries = []       #contains ExpandedQuery




def filterDependencies(file):       # This function is run via linux bash (feed in via PIPE) so file not necessary
    out = ""
    # uncomment to use a file input source
    # with open(path, mode='r', encoding='utf-8', errors=None) as file_in:
        #text = file_in.readlines() #readlines takes whole string up until newline character
        #for line in text:

    # or, instead of a file input, use stdin (pipe in command line)
    for line in sys.stdin:
        line = line.lower()
        if re.match(regexs[1], line):    # give me lines that aren't treebank lines
            out += line[:-1] + ".\n"            # StanfordParser gives me facts
        if re.match(regexs[2], line):
            out += line
    return out

if (sys.argv[1] != "parsed-queries.txt"):
    file_out = open (sys.argv[1], 'a')      # out, appends file
else:
    file_out = open (sys.argv[1], 'w+')     # out, (over)writes file

file_out.write(filterDependencies(None))    # in
file_out.close()

