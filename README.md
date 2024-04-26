# This directory contains a starter Flask project used in the Search tutorial.

note:
package version list:
elastic-transport==8.12.0
elasticsearch==8.12.0

but the elasticsearch version is 8.12.1
plugin smartcn in elasticsearch is compatible
plugin tsconvert v8.12.1 is compatible (in fact this plugin has to be compatible with es v8.12.1 in order to work and be installed)

# How to affect scoring system

1. in the search query API, using different analyzer for the respective content results in different scoring result.
2. in the info_analysis application, switching the value of search_analyzer and search_quote_analyzer field can make scoring different.

# note: limit

if you want to prioritize synonym list, you will be disappointed. The elastic search engine won't allow you to put synonym_graph filter during the index time.

and it makes sense, if user input query is in the synonym list and the synonym_graph filter is used immediately before the tokenizer is put into use, then the tokenizer becomes useless. We should see if the tokenizer helps then lookup the synonym list.
