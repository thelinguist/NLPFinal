# Factoid Question Answering using the Stanford NLP Parser
There are often times when humans need information, but a presented with a document or text that they don't want to read. It would be nice to ask a computer to read it and have it tell a user bits of information. For example, with a privacy policy for a website, it would be nice to just ask the computer if the policy protects the user's identity by not giving out identifiable information.
The Stanford NLP parser generates a list of dependencies for a natural language sentence, and can do this for a set of documents. The script "finalproject.sh" gets an argument of a text file containing a document to query and processes it using the Stanford NLP parser. The script then uses a set of input-queries, written in plain English in a text file ("inputqueries.txt") to go through the dependencies and answer questions about the document.
Currently the method is more of a proof of concept. There are some flaws, such as not being able to process information across sentences (such as a pronoun referring to something a couple sentences back), but it can extract relevant information to a query.
## Requirments
* bash
* python 3.5
* NLTK Module
* Stanford Parser 2015
* settings in the NLP Parser script to allow 1000m memory.
* SWI-Prolog 7.2.3

## Instructions
Create a directory with the above dependencies. 
Edit the NLP Parser script to allow more memory for the project (1000m is good). 
Specify your questions in a new line in a file called `inputqueries.txt` which might look something like this:
```
What can this program learn?
Who is the President of the United States?
```
specify input files. The input files currently reside in the Privacy Policy folders as .txt files
run the bash script `finalproject.sh`
it will generate some files, being a proof of concept, and generate `finally.txt` containing the answers to questions in a Prologue language format.

## Authors
* Myself

## Acknowledgements
* [Stanford NLP Parser](nlp.stanford.edu) for the powerful NLP toolset
* Dr. Lonsdale at BYU for the guidance
