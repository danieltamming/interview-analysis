# InterviewAnalysis
Scripts and functions to scrape and analyze text from [ASAP Sports](http://www.asapsports.com/), a sports interview transcript site. Thus far the code is focused entirely on practice day interviews between National Hockey League Stanley Cup Final games. The initial study of the data can be found in [this](https://medium.com/analytics-vidhya/a-quantitative-study-of-nhl-interviews-25b28821364b) Analytics Vidhya __Medium post__. I've published the dataset and an introductory notebook on [Kaggle](https://www.kaggle.com/dtamming/national-hockey-league-interviews). In the introductory notebook, *starter\_notebook.ipynb*, I contrast interviews with coaches and players and build a simple TFIDF-based model that determines whether a given interview transcript is coming from a coach or a player.

The functions (in bold below) that collect, clean, and access the data are well commented and written with other users in mind. 


### Code Files
__starter\_notebook.ipynb__:
 - explores and introduces the data, creates and tests a coach vs player classifier

___create\_csv.py___:
 - converts the html-tagged data into a Pandas dataframe, which is then saved as a csv

___scraper.py___:
 - scrapes interview data from the hockey portion of the site
 
___clean.py___:
 - corrects inconsistencies in the website's data

___utils.py___:
 - helper functions for gathering the scraped data

_plotting.py_:
 - creates figures that study these interviews 

### Data Files
data/interviews_raw.txt:
 - the scraped data

data/interviews_clean.txt:
 - the scraped data, cleaned using _clean.py_
 
 data/interview_data.csv:
 - the data from interviews_clean.txt, in a csv format

### Figures
Several of the figures contained in this repo are shown below. They are explained in detail in the Medium post <!-- [Medium post](<medium url>) -->.

![alt text](figures/player_sentiment.png)
![alt text](figures/coach_sentiment.png)
![alt text](figures/selfishness_histogram.png)
![alt text](figures/sentiment_histogram.png)
![alt text](figures/player_cloud.png)
![alt text](figures/coach_cloud.png)
