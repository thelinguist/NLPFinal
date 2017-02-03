#! /bin/bash
# By Bryce Shelley
# This script uses the Stanford NLP Parser and does the following:
#	1. parse through the sentences and create a dependency graph dependencies.txt
#       note: sentences may be too big, bump memory in lexparser.sh (1gb=200word sentence)
# 	2. filter the text for processing in prolog
#   2.5Combine parts into dependencies.txt --note that this is always appended
#   3. parse queries from a file and generate dependencies parsed-queries.txt
#	4. use prolog to send queries based on the queries.txt
#	5. return answers based on prolog's response
#
#   Usage Example: ./finalproject.sh policy-part1.txt policy-part2.txt
trap 'exit 130' INT             #this line stops the whole script on ctrl-c

if [ $1 = -h ];
    then
    echo "This script uses the Stanford NLP Parser to read the English Questions stored in inputQueries.txt. It outputs one or more files, but the results are contained in finally.txt"
    echo "To use this script: specify where the document is to be read. Don't forget to input the English questions into the inputQueries.txt before running the script."
    echo "example:"
    echo "./finalproject.sh policy.txt"
    echo ""
    echo "Other arguments:"
    echo "-t        Run the Test Script"
    echo "-h        Display this message"
else

    if [ $1 = -t ];
        # this block is for testing, usage: ./finalproject.sh -t PrivacyPolicies/testPolicy.txt
        then
        ./stanford-parser-full-2015-12-09/lexparser.sh $2 | python filter.py testDependencies.txt

    else
        for var
            do
            # STEP 1                                            |  STEP 2
            ./stanford-parser-full-2015-12-09/lexparser.sh $var | python filter.py dependencies.txt
            done
    fi

    # STEP 3
    ./stanford-parser-full-2015-12-09/lexparser.sh inputQueries.txt | python filter.py parsed-queries.txt

    # STEP 4
    if [ $1 = -t ];
        then
        python3.5 manual\ query\ building.py -t
    else
        python3.5 manual\ query\ building.py
    fi


    # STEP 5
    echo ""
    echo ""
    echo ""
    echo "--------------------RESULTS--------------------"
    cat finally.txt

fi