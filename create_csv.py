import numpy as np
import pandas as pd

from collections import Counter
from tqdm import tqdm
from bs4 import BeautifulSoup

def create_csv():
	file = 'data/interviews_clean.txt'
	with open(file) as f: 
		soup = BeautifulSoup(f, 'html.parser')
	df = pd.DataFrame(columns=['team1', 'team2', 'date', 
							   'name', 'job', 'text'])
	for entry in tqdm(soup.find_all('entry')):
		row = {}
		row['team1'] = entry.find('team1').text
		row['team2'] = entry.find('team2').text
		assert row['team1'] != row['team2']
		row['date'] = entry.find('date').text
		for answer in entry.find_all('answer'):
			inner_row = row.copy()
			name = answer.find('name').text
			if 'coach' in name:
				assert name.startswith('coach')
				inner_row['job'] = 'coach'
				name = name.split('coach ', 1)[1]
			else:
				inner_row['job'] = 'unknown'
			inner_row['name'] = name
			inner_row['text'] = answer.find('text').text
			assert not any(['<' in s for s in inner_row.values() 
							if isinstance(s, str)])
			df = df.append(inner_row, ignore_index=True)
	df.index.rename('RowId', inplace=True)
	df.to_csv('data/interview_data.csv')

def list_names():
	df = pd.read_csv('data/interview_data.csv').set_index('RowId')
	counts = df.name.value_counts().sort_values(
		ascending=False)
	for name in counts.index:
		print(name, counts.loc[name])

def fix_jobs():
	df = pd.read_csv('data/interview_data.csv').set_index('RowId')
	# undetected coach names, and names of people who are neither 
	# a coach nor a player that appear more than 10 times
	coach_names = ['terry murray', 'bruce cassidy', 'craig berube', 
				   'ken hitchcock']
	other_names = ['jamey horan', 'john madden', 'frank brown', 
				   'pierre mcguire', 'commissioner bettman', 'colin campbell',
				   'brian burke', 'gary bettman', 'peter chiarelli',
				   'bill daly', 'david keon', 'brian maclellan',
				   'steve yzerman', 'deputy commissioner daly',
				   'stan bowman', 'lou lamoriello', 'kerry mcgovern']
	for name in other_names[1:] + coach_names:
		assert name in df.name.unique(), name + ' not found in dataframe.'
	df.loc[df.name.isin(coach_names), 'job'] = 'coach'
	df.loc[df.name.isin(other_names), 'job'] = 'other'
	df.loc[df.job == 'unknown', 'job'] = 'player'
	df.loc[df.name == 'commissioner bettman', 'name'] = 'gary bettman'
	df.loc[df.name == 'deputy commissioner daly', 'name'] = 'bill daly'
	df.to_csv('data/interview_data.csv')

def fix_dtypes():
	df = pd.read_csv('data/interview_data.csv').set_index('RowId')
	print(df.memory_usage(index=True, deep=True).sum()/2**10)
	df['date'] = pd.to_datetime(df.date)
	df['job'] = df.job.astype('category')
	df['name'] = df.name.astype('category')
	df['team1'] = df.team1.astype('category')
	df['team2'] = df.team2.astype('category')
	print(df.memory_usage(index=True, deep=True).sum()/2**10)
	df.to_csv('data/interview_data.csv')

def merge_answers():
	df = pd.read_csv('data/interview_data.csv').set_index('RowId')
	df = df.dropna()
	df = df.groupby(['team1', 'team2', 'date', 'name', 'job'])['text'].apply(
		'. '.join).reset_index()
	df.index.rename('RowId', inplace=True)
	df.to_csv('data/interview_data.csv')

if __name__ == "__main__":
	create_csv()
	fix_jobs()
	fix_dtypes()
	merge_answers()

	# coach_names = ['terry murray', 'bruce cassidy', 'craig berube', 
	# 			   'ken hitchcock', 'stan bowman']
	# other_names = ['jamey horan', 'john madden', 'frank brown', 
	# 			   'pierre mcguire', 'commissioner bettman', 'colin campbell',
	# 			   'brian burke', 'gary bettman', 'peter chiarelli',
	# 			   'bill daly', 'david keon', 'brian maclellan',
	# 			   'steve yzerman']
	# df = pd.read_csv('data/interview_data.csv').set_index('RowId')
	# df['date'] = pd.to_datetime(df.date)
	# df['year'] = df.date.map(lambda x: x.year)
	# for year in sorted(df.year.unique()):
	# 	print(year, df[(df.year == year) & (df.job == 'coach')].name.unique())
