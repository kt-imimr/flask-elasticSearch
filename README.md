# Elasticsearch Search Tutorial

This directory contains a starter Flask project used in the Search tutorial.

# How to affect scoring system

1. in the search query API, using different analyzer for the respective content results in different scoring result.
2. in the info_analysis application, switching the value of search_analyzer and search_quote_analyzer field can make scoring different.

# note: limit

if you want to prioritize synonym list, you will be disappointed. The elastic search engine won't allow you to put synonym_graph filter during the index time.

and it makes sense, if user input query is in the synonym list and the synonym_graph filter is used immediately before the tokenizer is put into use, then the tokenizer becomes useless. We should see if the tokenizer helps then lookup the synonym list.
