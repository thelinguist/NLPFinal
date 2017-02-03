# Created by Bryce Shelley
# This is used in conjunction with the bash script finalproject.sh to allow a user to query a text with a given query
# and info file.

import re
import sys
from nltk.corpus import wordnet as wn
import os
import subprocess
from subprocess import call, PIPE, Popen
from subprocess import check_output

# Input Files
queriesIn = "parsed-queries.txt"
origQueries = "inputQueries.txt"
dependenciesFile = "dependencies.txt"

# Output Files
displayPrologQueries = "Queries For Prolog.txt"
finalResults = "finally.txt"

# global vars
longestSentence = 200 # estimated
regexs = ["^\(", "^\w", "\W$"]
expandedQueries = []       #contains ExpandedQuery


class Predicate:
    """
    an object that has a rule (dobj), and two parameters (watch, tv)
    """
    def __init__(self):
        self.rule = ""
        self.param1 = ""
        self.param1pos = -1
        self.param2 = ""
        self.param2pos = -1

    def __str__(self):
        return toString()

    def toString(self):
        out = self.rule + "("
        out += self.param1 + "-"
        out += str(self.param1pos) + ", "
        out += self.param2 + "-"
        out += str(self.param2pos) + ")."
        return out

    def toPred(self, fromString):
        """
        parse the predicate into an object
        :param fromString: the predicate as a string
        :return: None
        """
        parts = re.split("\(", fromString)
        self.rule = parts[0]
        parts = re.split("-", parts[1])
        self.param1 = parts[0]
        if len(parts) > 3:          # for words that have dashes in them
            extraDash = "-".join(parts[1:-1])
            parts = [parts[0], extraDash, parts[-1]]

        self.param1pos = re.split(",", parts[1])[0]
        self.param2 = re.split(",", parts[1])[1][1:]
        parts = re.split("\)", parts[2])
        self.param2pos = parts[0]




class ExpandedQuery:
    """
    A query that has a root line, list of arguments, and the argument to be queried
    """
    def __init__(self):
        self.rootP = Predicate()
        self.arguments = []
        self.argumentsP = [Predicate()]
        self.query = ""
        self.variations = [ExpandedQuery]    # can I put a list of ExpandedQueries here? probs... -- unused
        self.origQuestion = ""
        self.ynQuestion = False

    def addArg(self, argument):
        self.arguments.append(argument)

    def toString(self):
        out = "They\n"
        out += self.rootP.param2
        for argument in self.arguments:
            out += "\n" + argument
        out += "\n" + "??" + self.query
        out += "\npos: " + str(self.rootP.param2pos)
        return out


def gatherQueryParse(simpleQueries):
    gatheredQueries = []
    gatheredQuery = ""
    # save each line, until you come across a blank line
    for line in simpleQueries:
        if line != "\n":
            gatheredQuery += line
        elif gatheredQuery != "":
            gatheredQueries.append(gatheredQuery)
            gatheredQuery = ""

    return gatheredQueries


def getSynonyms(word):
    """
    swap verbs and direct objects from queries
    :param word: a verb
    :return: a list of synonyms
    """
    out = []
    # get synset of verb
    line = word
    if (len(line) > 0):
        oldWord = word
        for synset in wn.synsets(word, pos=wn.VERB):
            l = re.split('\.', str(synset))[0]
            l = re.split("\'", l)[1]
            out.append(re.sub(oldWord, l, line))
    return out


def getWord(word):
    word = re.split("[0-9]", word)[1]
    word = word[2:-1]
    return word


def addRelatedQuery(expandedQuery):
    """
    copy an expandedQuery and allow the rootVerb to be set to a variation, based on wordnet
    :param expandedQuery:
    :return: a list of ExpandedQuery objects, whose rootVerbs have been swapped with synonyms
    """
    out = []
    rootVariations = getSynonyms(expandedQuery.rootP.param2)

    #copy expanded query and replace root with variation(synonym)
    for variation in rootVariations:
        copy = expandedQuery
        if not copy.rootP.param2 == variation:
            copy.rootP.param2 = variation
            out.append(copy)
        del copy
    return out


def saveQueriesToFile():
    """
    This just saves the queries with the toString function
    """
    file_out = open("queriesThusFar.txt", "w+")
    for e in expandedQueries:
        file_out.write(e.toString() + "\n\n")
    file_out.close()


def writeRawPrologQueries(prologQueries):
    """
    save the prolog queries to file
    :param prologQueries: the queries formatted for a bash command
    :return: None
    """
    file_penult = open(displayPrologQueries, "w+")
    file_penult.write(prologQueries)
    file_penult.close()


def filterDependencies(path):
    """
    This function is run via linux bash (feed in via PIPE) so file not necessary
    :param path: the file to write this to
    :return: the output
    """
    out = []
    with open(path, mode='r', encoding='utf-8', errors=None) as file_in:
        text = file_in.readlines() #readlines takes whole string up until newline character
        for line in text:

        #for line in sys.stdin:
            line = line.lower()
            if re.match(regexs[1], line):    # give me lines that aren't treebank lines
                line = re.sub(":", "_",line)
                out.append(line[:-1] + "\n")            # StanfordParser gives me facts
            if re.match(regexs[2], line):
                line = re.sub(":", "_",line)
                out.append(line)
    return out


def dealWithYNQuestions(parsedQuery, thetaArgs):
    """
    Yes No Questions have a slightly different structure and set of relations
    :param parsedQuery: the query object to update
    :param thetaArg: the current set of relations
    :return: None
    """
    parsedQuery.ynQuestion = True
    for arg in thetaArgs:
        if len(arg) > 0:
            if re.match("root\(", arg):
                myPredicate = Predicate()
                myPredicate.toPred(arg)
                parsedQuery.rootP = myPredicate
            elif not re.match("^nsubj", arg):       # don't care about the subject of the sentence
                myPredicate = Predicate()
                myPredicate.toPred(arg)
                parsedQuery.argumentsP.append(myPredicate)
                parsedQuery.arguments.append(arg)


                # for each relation (This happens anyways)
                    # format to text
                    # check if all relations match up
                    # show true or false


def expandQueries(simpleQueries):
    """
    Save each parsed-query as an ExpandedQuery object, which includes semantic relations, etc.
    :param simpleQueries: a group of lines representing a parsed query (comes from the NLP parser)
    :return:  None
    """
    # organize the parsed queries by each question
    gatheredQueries = gatherQueryParse(simpleQueries)

    # use this file to align script data with original question
    with open(origQueries, mode='r', encoding='utf-8', errors=None) as file_origQ:
        questions = file_origQ.readlines()

    # get root
    iterator = 0
    for query in gatheredQueries:
        parsedQuery = ExpandedQuery()
        parsedQuery.arguments = []
        thetaArgs = re.split("\n", query)
        for thetaArg in thetaArgs:
            if re.match("^aux.*(will|do)", thetaArg):
                dealWithYNQuestions(parsedQuery, thetaArgs)
                break
            # if thetaArg begins with root
            if re.match("root\(", thetaArg):
                myPredicate = Predicate()
                myPredicate.toPred(thetaArg)
                parsedQuery.rootP = myPredicate
            # if thetaArg begins with det and has a WH-word
            elif re.match("(who|what|where|when|why|how)", thetaArg):    #uh oh, there are multiple instances here
                parsedQuery.query = thetaArg

            # else save all the arguments that I've eyeballed in results as relevant arguments
            elif re.match("dobj\(", thetaArg):
                parsedQuery.arguments.append(thetaArg)
            elif re.match("case\(", thetaArg):
                parsedQuery.arguments.append(thetaArg)
            elif re.match("nmod:", thetaArg):
                parsedQuery.arguments.append(thetaArg)

        parsedQuery.origQuestion = questions[iterator]
        #add the object
        if (hasattr(parsedQuery, "rootP")):
            expandedQueries.append(parsedQuery)


        del parsedQuery
        iterator+=1

# for testing:
if sys.argv[1] == "-t":
    dependenciesFile = "testDependencies.txt"


##############################################################
# STEP 1: create "expandedQuery" objects from a queries file #
##############################################################
expandQueries(filterDependencies(queriesIn))

aList = []     # expandedQueries gets updated into this list
for e in expandedQueries:
    aList.extend(addRelatedQuery(e))
for e in aList:
    expandedQueries.append(e)


# uncomment to save STEP 1 to file:
# saveQueriesToFile()


##############################################################
#    STEP 2: match query objects to the file with the info   #
##############################################################
with open(dependenciesFile, mode='r', encoding='utf-8', errors=None) as file_in:
    text = file_in.readlines()
    # for i, finishedQuery in enumerate(expandedQueries):
    for finishedQuery in expandedQueries:         #thanks Python, for making life difficult
        for line in text:
            if len(line) > 1:
                myPred = Predicate()
                myPred.toPred(line)
                if re.match("^root", line):
                    if re.search(finishedQuery.rootP.param2, line):
                        # extract the position in the sentence
                        finishedQuery.rootP.param2pos = myPred.param2pos
                        break                           # once found, break out of going thru by line
            # elif re.match("ccomp.*does", line):     # Parser issues with: "does verb." so this is my workaround.


# uncomment to show STEP 2:
# for other in expandedQueries:
#    print(other.toString())


##############################################################
#           STEP 3: create and send queries to Prolog        #
##############################################################
finalOutput = ""
manualQueries = ""
queryAttempt = ""
for finalQuery in expandedQueries:
    for thetaArg in finalQuery.arguments:
        # If it was found in the text to search
        if (finalQuery.rootP.param2pos != -1):
            statement = Predicate()
            statement.toPred(thetaArg)
            # TODO: add relations
            if (statement.rule == "dobj"):
                #for i in range[1,longestSentence]:
                    queryAttempt = statement.rule + "(" + statement.param1 + "-" + str(finalQuery.rootP.param2pos) + ", X)"
                    #queryAttempt = thetaArg[0:-3] + str(expandedQueries[0].position) + thetaArg[-2:]
                    #hit up the database
                    prologQuery = "\"%s, writeln(X), false\"" % queryAttempt

                    searchCommand = "swipl -q -s " + dependenciesFile + " -t " + prologQuery                # see: http://stackoverflow.com/questions/11234469/how-do-i-show-the-results-of-pattern-matching-goals-in-swi-prolog-from-a-shell-i?rq=1
                    manualQueries += searchCommand + "\n"
                    #commandList = ["swipl", "-q", "-s", dependenciesFile, "-t", prologQuery]
                    #pipe = subprocess.Popen(commandList, stdout=subprocess.PIPE)
                    #prologResult = pipe.communicate()[0]
                    prologResult = subprocess.Popen(searchCommand, shell=True, stdout=subprocess.PIPE).stdout.read()
                    #prologResult = check_output(["swipl", "-q", "-s", searchCommand])
                    #prologResult, error = check_output(["swipl", "-q", "-s", "parsed-queries.txt", "-t", "\"det(information-2, X), writeln(X), false\""])


                    finalOutput += finalQuery.origQuestion + "\n"
                    finalOutput += prologResult.decode("utf-8")
                    finalOutput += "--------------------------------------\n"


# uncomment to save STEP 3 to file:
# writeRawPrologQueries(manualQueries)


##############################################################
#                   OUTPUT THE RESULTS                       #
##############################################################
file_final = open(finalResults, "w+")
file_final.write(finalOutput)
file_final.close()