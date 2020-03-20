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
							   'name', 'is_coach', 'text'])
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
				inner_row['is_coach'] = True
				name = name.split('coach ', 1)[1]
			else:
				inner_row['is_coach'] = False
			inner_row['name'] = name
			inner_row['text'] = answer.find('text').text
			assert not any(['<' in s for s in inner_row.values() 
							if isinstance(s, str)])
			df = df.append(inner_row, ignore_index=True)
	df.index.rename('RowId', inplace=True)
	df.to_csv('data/interview_data.csv')

def list_names():
	df = pd.read_csv('data/interview_data.csv').set_index('RowId')
	counts = df[df.is_coach == False].name.value_counts().sort_values(
		ascending=False)
	for name in counts.index:
		print(name, counts.loc[name])

def fix_is_coach():
	df = pd.read_csv('data/interview_data.csv').set_index('RowId')
	# undetected coach names that appear more than 25 times
	coach_names = ['terry murray', 'bruce cassidy', 'craig berube']
	df.loc[df.name.isin(coach_names), 'is_coach'] = True
	df.to_csv('data/interview_data.csv')

if __name__ == "__main__":
	# create_csv()
	list_names()
	# fix_is_coach()