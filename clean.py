import re
import argparse
import nltk
from bs4 import BeautifulSoup
from collections import Counter

def parsing():
	parser = argparse.ArgumentParser()
	parser.add_argument('-tgt', '--targfile', default='cleaned_data.txt', 
						type=str, help='File to write cleaned data to?')
	parser.add_argument('-raw', '--rawfile', default='raw_data.txt',
						type=str, help='Raw data file?')
	return parser.parse_args()

def get_input_name(name):
	'''
	Get first name of coach from user
	'''
	usr_input = None
	while usr_input != 'y' and usr_input != 'Y':
		input_name = input('Enter coach '+name[0]+'\'s first name: ')
		full_name = 'coach ' + input_name + ' ' + name[0]
		usr_input = input('Name will be changed to: \''+full_name+'\'. Enter Y to continue: ')
	return full_name

def get_input_approval(name, target_name):
	'''
	Get user approval to change name
	'''
	usr_input = input('Enter Y to approve name change from \''+name+'\' to \''+target_name+'\': ')
	return usr_input == 'y' or usr_input == 'Y'

def clean_coach_names():
	'''
	In the scraped data oaches's name is in any of three formats.
	Combines the three formats into 'coach <firstname> <lastname>'
	with user input, and writes the cleaned data to a file specified by the user
	'''
	args = parsing()
	with open(args.rawfile) as f:
		soup = BeautifulSoup(f, 'html.parser')
	coach_tags = soup.find_all('name', text = re.compile('coach'))
	coach_names = sorted([coach.text.split()[1:] for coach in set(coach_tags)], key = lambda x: x[-1])
	coach_names_full = [name for name in coach_names if len(name) == 2]
	coach_names_last = [name[0] for name in coach_names if len(name) == 1]
	for name in coach_names_last:
		if name in [name[-1] for name in coach_names_full]: 
			coach_names.remove([name])
	
	for name in coach_names:
		last_name = name[-1]
		if len(name) == 2: target_name = 'coach ' + ' '.join(name)
		else: target_name = get_input_name(name)

		length = len(soup.find_all('name', text = re.compile(target_name)))

		shared_names = set([tag.text for tag in soup.find_all('name', text = re.compile(last_name))]).difference([target_name])
		for name in shared_names:
			usr_approved = get_input_approval(name, target_name)
			regex_name = '^' + name + '$'
			if usr_approved: 
				length += len(soup.find_all('name', text = re.compile(regex_name)))
				for name_tag in soup.find_all('name', text=re.compile(regex_name)):
					name_tag.string.replace_with(target_name)
		assert len(soup.find_all('name', text = re.compile(target_name))) == length

	with open(args.targfile, 'w') as f:
		f.write(str(soup))


clean_coach_names()