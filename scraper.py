import re
import requests
import string
import argparse
from tqdm import tqdm
from bs4 import BeautifulSoup, Comment

COUNT = 0

def parsing():
	parser = argparse.ArgumentParser()
	parser.add_argument('-tgt', '--targfile', default='scraperesults.txt', 
						type=str, help='File to write scraped data to?')
	parser.add_argument('-url', '--website', type=str, help='Sport page URL?',
						default='http://www.asapsports.com/showcat.php?id=5')
	return parser.parse_args()

def is_answer_start(s):
	# true iff first n words are capitalized and followed by a colon
	n = 4
	words = s.split(' ',n)[:-1]
	for word in words:
		if word.isupper() and word.endswith(':'): return True
	return False

def join_answers(answers):
	'''
	Parameter: list of answer string
	Returns: list of answer, unnamed answers appended to the previous answer
	Ensures each answer is begins with the name of the speaker
	'''
	if len(answers) == 0: return []
	for idx, ans in enumerate(answers):
		if ans.split(' ',1)[0].isupper(): break
	joined_answers = [answers[idx]]

	for answer in answers[idx+1:]:
		if not is_answer_start(answer):
			joined_answers[-1] += answer
		else:
			joined_answers.append(answer)
	return joined_answers

def clean_string(s):
	'''
	Parameter: string
	Returns: string lowercase, punctuation replaced with spaces
	'''
	to_remove = string.digits + ''.join([punc for punc in string.punctuation 
										 if punc != '\''])
	trans = str.maketrans(to_remove, len(to_remove)*' ')
	s = s.translate(trans).strip('\r\n\t ').lower()
	s = re.sub(' +', ' ', s)
	return s

def get_answers(soup, main_text):
	tags = main_text.find_all(text=True, recursive=False) + soup.find_all('p')
	tags = [tag for tag in tags if tag.string 
			and not isinstance(tag, Comment)]
	strings = [str(tag.string).strip('\r\n\t ') for tag in tags]
	answers = [s for s in strings if len(s) > 3 and s[:2] != 'Q.' 
			   and 'MODERATOR' not in s and 'FastScripts' not in s]
	return answers

def parse_interview(url):
	'''
	Parameters:	url of interview
	Returns:	data, list of (person's name, person's answer) tuples
	'''
	page = requests.get(url)
	soup = BeautifulSoup(page.text, 'html.parser')
	main_text = soup.find(attrs={'style':'padding: 10px;', 'valign':'top'})
	date = main_text.find('h2').get_text()

	for bold_tag in soup.find_all('b'): bold_tag.clear()
	answers = get_answers(soup, main_text)
	joined_answers = join_answers(answers)

	named_answers = []
	for i, answer in enumerate(joined_answers):
		person, statement = answer.split(':',1)
		person = clean_string(person)
		statement = clean_string(statement).split()
		named_answers.append((person, statement))

	global COUNT
	COUNT += 1

	return date, named_answers

def parse_name_page(url):
	'''
	Parameters:	url of page with links to each interviewee
	Returns:	list of parse_interview's return values
	'''
	page = requests.get(url)
	soup = BeautifulSoup(page.text, 'html.parser')
	table = soup.find('table', attrs={'width':'100%', 'cellspacing':'0', 
									  'cellpadding':'3', 'border':'0'})
	links = table.find_all('a', href=True)
	interviews = [parse_interview(link['href']) for link in links]
	return interviews

def parse_events_page(url):
	'''
	Parameters:	url of page with links to list of interviewees (name_page)
	Returns:	list of parse_name_page's return values
	'''
	page = requests.get(url)
	soup = BeautifulSoup(page.text, 'html.parser')
	table = soup.find('table', attrs={'width':'100%', 'cellspacing':'0', 
									  'cellpadding':'3', 'border':'0'})
	links = table.find_all('a', href=True)
	interviews_yearly = []
	for link in links:
		interviews_yearly.extend(parse_name_page(link['href']))
	return interviews_yearly

def parse_year_page(url):
	'''
	Parameters: url of page with year's hockey events
	Returns:	tuple of team names and url of stanley cup page, if they exist
	'''
	def scf_in_text(tag):
		return tag.name == 'a' and 'NHL STANLEY CUP FINAL' in tag.get_text()
	page = requests.get(url)
	soup = BeautifulSoup(page.text, 'html.parser')
	link = soup.find(scf_in_text)
	if link:
		matchup = link.get_text().split(': ')[-1].lower()
		teams = tuple(re.split(r'\sv\s|\svs\s', matchup))
		url = link['href']
		return teams, url
	return False, False


def parse_sport_page(url):
	'''
	Parameters: url of hockey page
	Returns:	list of urls for each year page
	'''
	page = requests.get(url)
	soup = BeautifulSoup(page.text, 'html.parser')
	table = soup.find_all('table', attrs={'width':'100%', 'cellspacing':'0', 
										  'cellpadding':'5', 'border':'0'})[1]
	links = table.find_all('a', href=True)
	urls = {}
	for link in links:
		teams, url = parse_year_page(link['href'])
		if url: 
			key = (link.get_text(), teams)
			urls[key] = url
	return urls

def get_data(url):
	'''
	Parameters: url of ASAP Sports sport page
	Returns: list of (team, team), data, named_answers
			where named_answers is a list of (person, person's answer) tuples
	'''
	year_urls = parse_sport_page(url)
	all_interviews = []
	for (year, teams), url in tqdm(year_urls.items()):
		interviews_yearly = parse_events_page(url)
		for date, named_answers in interviews_yearly:
			all_interviews.append((teams, date, named_answers))
	return all_interviews

def save_data(all_interviews, target_file):
	'''
	Parameters: file to write scraped data to, results of get_data
	Returns: none, but saves data in html format to target_file
	'''
	f = open(target_file, 'w+')
	for (team1, team2), date, named_answers in all_interviews:
		f.write('<entry>')
		f.write('<team1>'+team1+'</team1>')
		f.write('<team2>'+team2+'</team2>')
		f.write('<date>'+date+'</date>')
		for person, text in named_answers:
			f.write('<answer>')
			f.write('<name>'+person+'</name>')
			f.write('<text>'+' '.join(text)+'</text>')
			f.write('</answer>')
		f.write('</entry>')
	f.close()

if __name__ == "__main__":
	args = parsing()
	all_interviews = get_data(args.website)
	if input('Save Data?\n').lower() == 'y':
		save_data(all_interviews, args.targfile)
	else:
		print('Not saving data.')
	print(COUNT)