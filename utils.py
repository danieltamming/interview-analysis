import re
import math
import nltk
import numpy as np

from collections import Counter
from tqdm import tqdm
from bs4 import BeautifulSoup
from nltk.corpus import stopwords
from PIL import Image

exclude_names = set(['pierre mcguire', 'jamey horan', 'gary bettman', 'bill daly', 'frank brown', 'david keon', 'brian maclellan', 'bruce cassidy', 'craig berube', 'terry murray'])

def check_duplicates(L):
	count = 0
	for i in range(len(L)-1):
		for j in range(i+1, len(L)):
			if L[i] == L[j]: count += 1
	print(count)

def get_common_no_stop(words):
	'''
	Parameters: list of words, size of return list
	Returns: list of length n of (word, frequency)
	'''
	stop_words = set(nltk.corpus.stopwords.words('english'))
	words = [word for word in words if word not in stop_words]
	word_count = Counter(words)
	return word_count

def get_log_odds(dist1, dist2):
	'''
	Parameters: two nltk frequency distributions
	Returns: sorted list of (key, log odds of key)
	Higher log odds value corresponds to higher frequency in dist1
	'''
	total1, total2 = sum(dist1.values()), sum(dist2.values())
	grams = set(dist1.keys()).intersection(set(dist2.keys()))
	log_odds_list = len(grams)*[None]
	for i, key in enumerate(grams):
		ratio = math.log((float(dist1[key]+1)/(total1+1))/(float(dist2[key]+1)/(total2+1)))
		ratio = round(ratio, 5)
		log_odds_list[i] = (key, ratio)
	log_odds_list = sorted(log_odds_list, key = lambda x: x[1])
	return log_odds_list

def get_shannon_entropy(dist):
	'''
	Parameters: nltk frequency distribution (list of words and their frequency)
	Returns: 	scaled Shannon entropy of the distribution
	'''
	entropy = 0
	k = len(dist)
	total = sum(dist.values())
	for val in dist.values():
		val = float(val)
		entropy += (val/total)*math.log(total/val)
	return entropy/math.log(k)

def get_interviews_from(soup, name, all_together=True, limit=None):
	'''
	Parameters: person's name
	Returns: List of lists of words, the sublists are for each date interviewed
	Note: Some entries have multiple answer tags for a signle person,
			so we merge the text from these tags
	'''
	name_tags = soup.find_all('name', text=name) # all name tags with name
	entry_tags = set([tag.parent.parent for tag in name_tags]) # all entry tags containing interviews with name
	interviews = []
	for entry_tag in entry_tags:
		interview = []
		name_tags = entry_tag.find_all('name', text=name)
		for name_tag in name_tags:
			text = name_tag.next_sibling.text
			interview.extend(text.split())
		if all_together: interviews.extend(interview)
		else: interviews.append(interview)
		if limit and len(interviews) > limit: break
	if limit: interviews = interviews[:limit]
	return interviews

def get_word_counts(soup, names):
	word_counts = Counter()
	for name in names:
		count = 0
		for tag in soup.find_all('name', text=name):
			count += len(tag.next_sibling.text.split())
		word_counts[name] = count
	return word_counts

def get_most_common_names(soup, num_people, text_requirement=None):
	name_tags = soup.find_all('name', text=text_requirement)
	# names = set([tag.string for tag in name_tags if tag.string not in exclude_names])
	# interview_count = Counter()
	# for name in tqdm(names):
	# 	this_name_tags = soup.find_all('name', text_requirement=name)
	# 	interview_count[name] = len(set([tag.parent.parent for tag in this_name_tags]))
	# names = [item[0] for item in interview_count.most_common(num_people)]
	names = [tag.text for tag in name_tags if tag.text not in exclude_names]
	answer_count = Counter(names)
	names = [item[0] for item in answer_count.most_common(num_people)]
	return names

def get_all_words(soup, names, limit=None):
	all_words = []
	for name in tqdm(names):
		interviews = get_interviews_from(soup, name, limit=limit)
		# interview_words = [word for interview in interviews for word in interview]
		all_words.extend(interviews)
	return all_words

def get_words_by_year(soup, year, limit=None):
	date_tags = soup.find_all('date', text=re.compile(str(year)))
	entry_tags = [tag.parent for tag in date_tags]
	name_tags = []
	for entry_tag in entry_tags:
		name_tags.extend([tag for tag in entry_tag.find_all('name',) if tag.text not in exclude_names])
	# print(set([tag.text for tag in name_tags]))
	text_tags = [tag.next_sibling for tag in name_tags]
	words = []
	for tag in text_tags:
		words.extend(tag.text.split())
	if limit: words = words[:limit]
	return words

def process_player_mask():
	'''
	Turns the player silhouette picture into a mask
	'''
	mask = np.array(Image.open('figures/player_silhouette.jpg'))
	transformed_mask = np.ndarray((mask.shape[0],mask.shape[1]), np.int32)
	for i in range(mask.shape[0]):
		for j in range(mask.shape[1]):
			if mask[i,j] <= 10:
				transformed_mask[i,j] = 0
			else:
				transformed_mask[i,j] = 255

	print(transformed_mask.shape)
	img = Image.fromarray(transformed_mask)
	img.show()
	np.save('data/player_mask.npy',transformed_mask)

def process_coach_mask():
	'''
	Turns the coach silhouette picture into a mask
	'''
	mask = np.array(Image.open('figures/coach_silhouette.png'))
	transformed_mask = np.ndarray((mask.shape[0],mask.shape[1]), np.int32)
	for i in range(mask.shape[0]):
		for j in range(mask.shape[1]):
			if mask[i,j,0] <= 10:
				transformed_mask[i,j] = 255
			else:
				transformed_mask[i,j] = 0

	print(transformed_mask.shape)
	img = Image.fromarray(transformed_mask)
	img.show()
	np.save('data/coach_mask.npy',transformed_mask)