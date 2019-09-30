# InterviewAnalysis
Scripts and function to scrape text from [ASAP Sports](http://www.asapsports.com/), a sports interview transcript site. 
The resulting study can be found in a Medium post <!-- [this](<medium url>) Medium post. -->. 

The functions that collect, clean, and access the data  are well commented and written with other users in mind. 

Those whose sole interest is in the data itself need only to use data/interviews_clean.txt, although _utils.py_ provides useful helper functions. 

_scraper.py_:
 - scrapes interview data from the hockey portion of the site
 
_clean.py_:
 - corrects inconsistencies in the website's data

_plotting.py_:
 - creates figures that shed light on the nature of these interviews 

_utils.py_:
 - helper functions for gathering the scraped data

data/interviews_raw.txt:
 - the scraped data

data/interviews_clean.txt:
 - the scraped data, cleaned using clean.py
 
## Figures
Several of the figures contained in this repo are shown below. They are explained in detail in the Medium post <!-- [Medium post](<medium url>) -->.

![alt text](figures/player_cloud.png)
![alt text](figures/coach_cloud.png)
![alt text](figures/player_sentiment.png)
![alt text](figures/coach_sentiment.png)
![alt text](figures/selfishness_histogram.png)
![alt text](figures/sentiment_histogram.png)
