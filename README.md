# Description

This is made of two scripts, a crawler, and a parser. 
The crawler takes in parameters loads the page and feed it to the parser.
The parser then calls back the data to the crawler which saves it.

This is not the most beautiful code ever, but it does the Job.

# Usage
```
Usage: wiki_crawler.py [options]

Options:
  -h, --help            show this help message and exit
  -p, --pagelist        Parse the team page list.
  -r, --results         Parse the team page list.
  -i, --infos           Parse the team page list.
  -c, --contributions   Parse the team page list.
  -v, --pageview        Parse the team page views.
  -t, --text            Extract the team pages text.
  -b, --bioparts        Extract the team bioparts.
  -d, --redo            Relaunch parsing for team that had an error
                        previously.
  -y YEARS, --years=YEARS
                        List of years to parse separated by a comma (ex:
                        2012,2016)
```

# Dependencies
Python libraries:
* HTMLParser
* pandas
* boilerpipe
* progressbar
* nltk
* numpy
* scipy
