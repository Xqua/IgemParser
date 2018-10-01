# Description

Code repository to parse the igem websites, different APIs, result pages, biobricks etc.

The main script is: `wiki_crawler`

# Usage
```
Usage: wiki_crawler.py [options]

Options:
  -h, --help            show this help message and exit
  -p, --pagelist        Parse the team page list.
  -r, --results         Parse the team page list.
  -i, --infos           Parse the team page list.
  -v, --pageview        Parse the team page views.
  -t, --text            Extract the team pages text.
  -b, --bioparts        Extract the team bioparts.
  -n, --networks        Extract the intra and inter team network data.
  -a, --append          Append to already existing database files.
  -y YEARS, --years=YEARS
                        List of years to parse separated by a comma (ex:
                        2012,2016)

```

# Other scripts
- `wiki_parser` contains a couple HTMLParser classes to parse some iGEM pages into utilizable RESULTS
- `networks` contains a class that uses the mediawiki API to parse the different contributions, along with the content of the teams wiki in order to create the different collaboration networks.
- `merged_results` In case one needs to merge different years together or different databases together:

## merged_results Usage:

```Usage: merge_results.py [options]

Options:
  -h, --help            show this help message and exit
  -r FOLDERS, --result-folders=FOLDERS
                        result folder to merge. -r folder1 -r folder2 etc
  -o OUT, --out-path=OUT
                        out folder path to store merged_results into.
  -c, --check           Compare number of team to registered number of teams
                        per year.
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
* fuzzywuzzy
* BeautifulSoup4
