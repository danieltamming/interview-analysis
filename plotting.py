import re
import math
import nltk
import numpy as np
import matplotlib.pyplot as plt

from collections import Counter
from tqdm import tqdm
from bs4 import BeautifulSoup
from afinn import Afinn
from wordcloud import WordCloud
from utils import *


def players_vs_coaches():
	coach_names = get_most_common_names(soup, 20, text_requirement=re.compile('coach'))
	player_names = get_most_common_names(soup, 20, text_requirement=re.compile('^((?!coach).)*$'))
	coach_word_counts = get_word_counts(soup, coach_names)
	player_word_counts = get_word_counts(soup, player_names)
	min_word_count = min(list(coach_word_counts.values()) + list(player_word_counts.values()))
	coach_words = get_all_words(soup, coach_names, limit=min_word_count)
	player_words = get_all_words(soup, player_names, limit=min_word_count)
	n = 1
	ngs_player = nltk.ngrams(player_words, n)
	fdist_player = nltk.FreqDist(ngs_player)
	ngs_coach = nltk.ngrams(coach_words, n)
	fdist_coach = nltk.FreqDist(ngs_coach)
	log_odds_list = get_log_odds(fdist_player, fdist_coach)
	player_entropy = get_shannon_entropy(fdist_player)
	coach_entropy = get_shannon_entropy(fdist_coach)
	# higher value is player
	print(log_odds_list[:10])
	print()
	print(log_odds_list[-10:])
	print()
	print(player_entropy)
	print()
	print(coach_entropy)

def compare_years():
	limit = 16493

	years = [year for year in range(1997, 2020) if year not in [2005, 2008]]
	entropies = []
	dict_size = []
	sentiment = []
	afinn = Afinn()
	for year in tqdm(years):
		words = get_words_by_year(soup, year, exclude_names)
		fdist = nltk.FreqDist(words)
		shannon_entropy = get_shannon_entropy(fdist)
		entropies.append(shannon_entropy)
		dict_size.append(len(set(words)))
		sentiment.append(afinn.score(' '.join(words)))

	# plt.figure()
	# plt.xlabel('Year')
	# plt.ylabel('Shannon Entropy')
	# plt.plot(years, entropies, 'o')
	# plt.show()
	plt.figure()
	plt.xlabel('Year')
	plt.ylabel('Sentiment')
	plt.plot(years, sentiment, 'o')
	plt.show()

def sentiment_boxplot(names, wins, coaches):
	exclude_names = set(['pierre mcguire', 'jamey horan', 'gary bettman', 'bill daly', 'frank brown', 'david keon', 'brian maclellan', 'bruce cassidy', 'craig berube', 'terry murray'])

	afinn = Afinn()

	results = len(names)*[None]

	for i, name in enumerate(tqdm(names)):
		interviews = get_interviews_from(soup, name, all_together=False)
		sentiments = len(interviews)*[0]
		for j, interview in enumerate(interviews):
			sentiments[j] = afinn.score(' '.join(interview))/len(interview)
		results[i] = (names[i], sorted(sentiments))

	colors = ['cyan', 'lightblue', 'lightgreen', 'tan', 'beige']
	position_list = list(range(len(names)))
	fig, ax = plt.subplots()
	subplts = []
	win_set = sorted(list(set([tup[1] for tup in wins])))

	for win_count, color in zip(win_set, colors):
		selected_names = [tup[0] for tup in wins if tup[1] == win_count]
		data = [result[1] for result in results if result[0] in selected_names]
		label_names = [name.split(' ',1)[1] for name in selected_names] if coaches else selected_names
		subplt = ax.boxplot(data, positions=position_list[:len(selected_names)], 
			vert=0, labels=label_names, patch_artist=True, widths=0.25)
		subplts.append(subplt)
		del position_list[:len(selected_names)]
		for patch in subplt['boxes']: patch.set_facecolor(color)
	pos = ax.get_position()
	# ax.set_position([pos.x0, pos.y0+0.1*pos.height, pos.width, 0.9*pos.height])
	ax.legend(reversed([subplt['boxes'][0] for subplt in subplts]), reversed(win_set),
				title='Legend: # of Stanley Cup Wins', loc='lower left', bbox_to_anchor=(0,1.02,1,0.2),
				fancybox=False, ncol=len(win_set), mode='expand', borderaxespad=0)
	title_text = 'Sentiment of 10 Most Interviewed Coaches' if coaches else 'Sentiment of 10 Most Interviewed Players'
	# plt.title(title_text, y=1.2, fontweight='bold')
	plt.ylabel('Name', fontweight='bold')
	plt.xlabel('Sentiment Score', fontweight='bold')
	plt.tight_layout()
	figure_name = 'coach_sentiment' if coaches else 'player_sentiment'
	figure_name += '_no_title'
	plt.savefig('figures/'+figure_name+'.png')
	plt.show()

def sentiment_histogram(player_names, coach_names):
	exclude_names = set(['pierre mcguire', 'jamey horan', 'gary bettman', 'bill daly', 'frank brown', 'david keon', 'brian maclellan', 'bruce cassidy', 'craig berube', 'terry murray'])
	afinn = Afinn()

	fig, ax = plt.subplots()
	plt.ylabel('# of Interviews')
	plt.xlabel('Sentiment Score')
	plt.title('Sentiment Distribution')

	for idx, names in enumerate([player_names, coach_names]):
		if idx == 0:
			hist_color = 'lightblue'
			plot_form = '--b'
			histlabel = 'Players'
			plotlabel = 'Players Normal Approx. \n'
		else:
			hist_color = 'lightgreen'
			plot_form = '--g'
			histlabel = 'Coaches'
			plotlabel = 'Coaches Normal Approx. \n'

		sentiments = []
		for i, name in enumerate(tqdm(names)):
			interviews = get_interviews_from(soup, name, all_together=False, limit=8)
			his_sentiments = len(interviews)*[0]
			for j, interview in enumerate(interviews):
				his_sentiments[j] = afinn.score(' '.join(interview))/len(interview)
			sentiments.extend(his_sentiments)

		sent = np.array(sentiments)
		n, bins, patches = ax.hist(sent, alpha=0.25, range=(-0.05,0.25), bins=30, color=hist_color, label=histlabel)
		mu, sigma = sent.mean(), sent.std()
		y = ((1 / (np.sqrt(2 * np.pi) * sigma)) *
     			np.exp(-0.5 * (1 / sigma * (bins - mu))**2))
		plotlabel += ' (' + r' $\mu$ = ' + str(round(mu,3)) + r', $\sigma$ = ' + str(round(sigma,3)) + ')'
		ax.plot(bins, y, plot_form, label=plotlabel)
	handles, labels = ax.get_legend_handles_labels()
	plt.legend(reversed(handles), reversed(labels), loc='upper right')
	plt.tight_layout()
	plt.savefig('sentiment_histogram.png')
	plt.show()

def selfish_boxplot(names, lexicon, wins, coaches):
	results = len(names)*[None]
	for i, name in enumerate(tqdm(names)):
		interviews = get_interviews_from(soup, name, all_together=False)
		sentiments = len(interviews)*[0]
		for j, interview in enumerate(interviews):
			sentiments[j] = sum([lexicon[word] for word in interview])/len(interview)
		results[i] = (names[i], sorted(sentiments))

	colors = ['cyan', 'lightblue', 'lightgreen', 'tan', 'beige']
	position_list = list(range(len(names)))
	fig, ax = plt.subplots()
	subplts = []
	win_set = sorted(list(set([tup[1] for tup in wins])))

	for win_count, color in zip(win_set, colors):
		selected_names = [tup[0] for tup in wins if tup[1] == win_count]
		data = [result[1] for result in results if result[0] in selected_names]
		label_names = [name.split(' ',1)[1] for name in selected_names] if coaches else selected_names
		subplt = ax.boxplot(data, positions=position_list[:len(selected_names)], 
			vert=0, labels=label_names, patch_artist=True, widths=0.25)
		subplts.append(subplt)
		del position_list[:len(selected_names)]
		for patch in subplt['boxes']: patch.set_facecolor(color)
	pos = ax.get_position()
	# ax.set_position([pos.x0, pos.y0+0.1*pos.height, pos.width, 0.9*pos.height])
	ax.legend(reversed([subplt['boxes'][0] for subplt in subplts]), reversed(win_set),
				title='Legend: # of Stanley Cup Wins', loc='lower left', bbox_to_anchor=(0,1.02,1,0.2),
				fancybox=False, ncol=len(win_set), mode='expand', borderaxespad=0)
	title_text = 'Selfishness of 10 Most Interviewed ' 
	title_text += 'Coaches' if coaches else 'Players'
	# plt.title(title_text, y=1.2, fontweight='bold')
	plt.ylabel('Name', fontweight='bold')
	plt.xlabel('Selfishness Score', fontweight='bold')
	plt.tight_layout()
	figure_name = 'coach_selfishness' if coaches else 'player_selfishness'
	# plt.savefig('figures/'+figure_name+'.png')
	plt.show()

def selfishness_histogram(player_names, coach_names, lexicon):
	exclude_names = set(['pierre mcguire', 'jamey horan', 'gary bettman', 'bill daly', 'frank brown', 'david keon', 'brian maclellan', 'bruce cassidy', 'craig berube', 'terry murray'])

	fig, ax = plt.subplots()
	plt.ylabel('# of Interviews')
	plt.xlabel('Selfishness Score')
	plt.title('Selfishness Distribution')

	for idx, names in enumerate([player_names, coach_names]):
		if idx == 0:
			hist_color = 'lightblue'
			plot_form = '--b'
			histlabel = 'Players'
			plotlabel = 'Players Normal Approx. \n'
		else:
			hist_color = 'lightgreen'
			plot_form = '--g'
			histlabel = 'Coaches'
			plotlabel = 'Coaches Normal Approx. \n'

		selfishness = []
		for i, name in enumerate(tqdm(names)):
			interviews = get_interviews_from(soup, name, all_together=False, limit=8)
			his_selfishness = len(interviews)*[0]
			for j, interview in enumerate(interviews):
				his_selfishness[j] = sum([lexicon[word] for word in interview])/len(interview)
			selfishness.extend(his_selfishness)

		sent = np.array(selfishness)
		n, bins, patches = ax.hist(sent, alpha=0.5, range=(-0.15,0.12), bins=30, color=hist_color, label=histlabel)
		mu, sigma = sent.mean(), sent.std()
		y = ((1 / (np.sqrt(2 * np.pi) * sigma)) *
     			np.exp(-0.5 * (1 / sigma * (bins - mu))**2))
		plotlabel += ' (' + r' $\mu$ = ' + str(round(mu,3)) + r', $\sigma$ = ' + str(round(sigma,3)) + ')'
		ax.plot(bins, y, plot_form, label=plotlabel)
	handles, labels = ax.get_legend_handles_labels()
	plt.legend(reversed(handles), reversed(labels), loc='upper right')
	plt.tight_layout()
	plt.savefig('figures/selfishness_histogram2.png')
	plt.show()

def scatter_selfishness_sentiment(coach_names, player_names, lexicon):
	names = coach_names + player_names
	afinn = Afinn()

	fig, ax = plt.subplots()
	plt.ylabel('Sentiment')
	plt.xlabel('Selfishness')
	# plt.title('')
	hist_color = 'lightgreen'
	plot_form = '--g'
	histlabel = 'Coaches'
	plotlabel = 'Coaches Normal Approx. \n'

	# results = len(names)*[None]
	selfishness, sentiments = len(names)*[0], len(names)*[0]
	for i, name in enumerate(tqdm(names)):
		words = get_interviews_from(soup, name, all_together=True)
		his_selfishness = sum([lexicon[word] for word in words])/len(words)
		his_sentiment = afinn.score(' '.join(words))/len(words)
		# results[i] = (name, selfishness, sentiment)
		selfishness[i] = his_selfishness
		sentiments[i] = his_sentiment

	ax.scatter(selfishness, sentiments)
	for name,x,y in zip(names, selfishness, sentiments):
		ax.annotate(name, (x,y), xytext=(0,10), textcoords='offset points', ha='center')
	# handles, labels = ax.get_legend_handles_labels()
	# plt.legend(reversed(handles), reversed(labels), loc='upper right')
	# plt.tight_layout()
	# plt.savefig('figures/selfishness_histogram2.png')
	plt.show()

def log_odds_word_cloud(coach_names, player_names, n=1, num_words=30):
	fdists = 2*[None]
	for i, names in enumerate([player_names, coach_names]):
		words = []
		for name in tqdm(names):
			interviews = get_interviews_from(soup, name, all_together=False, limit=8)
			words.extend([word for interview in interviews for word in interview])
		ngs = nltk.ngrams(words, n)
		fdists[i] = nltk.FreqDist(ngs)

	log_odds_list = get_log_odds(fdists[0], fdists[1])

	print(fdists[0]['coach'])
	print(fdists[1]['coach'])

	for i in range(2):
		# first is coaches second is players
		log_odds = log_odds_list[:num_words] if i == 0 else log_odds_list[-num_words:]
		weights = {word: freq for (word,), freq in log_odds}
		my_wordcloud = WordCloud().generate_from_frequencies(weights)
		plt.imshow(my_wordcloud, interpolation='bilinear')
		plt.axis('off')
		plt.show()

def word_cloud(names, mask_file, save_file, n=1, num_words=40):
	cloud_mask = np.load(mask_file)
	words = []
	for name in tqdm(names):
		interviews = get_interviews_from(soup, name, all_together=False, limit=8)
		words.extend([word for interview in interviews for word in interview])
	word_count = get_common_no_stop(words)
	my_wordcloud = WordCloud(max_words=num_words, mask=cloud_mask, contour_width=3, contour_color='black', background_color='white').generate_from_frequencies(word_count)
	plt.imshow(my_wordcloud, interpolation='bilinear')
	plt.axis('off')
	plt.show()
	my_wordcloud.to_file('figures/'+save_file)

file = 'data/interviews_clean.txt'
with open(file) as f: soup = BeautifulSoup(f, 'html.parser')
exclude_names = set(['pierre mcguire', 'jamey horan', 'gary bettman', 'bill daly', 'frank brown', 'david keon', 'brian maclellan', 'bruce cassidy', 'craig berube', 'terry murray'])

# coach_names = get_most_common_names(soup, 10, text_requirement=re.compile('coach'))
# player_names = get_most_common_names(soup, 10, text_requirement=re.compile('^((?!coach).)*$'))

# coach_wins = {'coach peter laviolette': 1, 'coach mike babcock': 1, 'coach larry robinson': 1, 'coach ken hitchcock': 1, 'coach mike sullivan': 2, 'coach scotty bowman': 9, 'coach darryl sutter': 2, 'coach pat burns': 1, 'coach claude julien': 1, 'coach joel quenneville': 3}
coach_wins = [('coach peter laviolette',1),('coach mike babcock',1),('coach larry robinson',1),('coach ken hitchcock',1),('coach mike sullivan',2),('coach scotty bowman',9),('coach darryl sutter',2),('coach pat burns',1),('coach claude julien',1),('coach joel quenneville',3)]
player_wins = [('scott stevens',3),('chris pronger',1),('martin brodeur',3),('sidney crosby',3),('paul kariya',0),('steve yzerman',3),('brett hull',2), ('j s  giguere',1), ('scott niedermayer',4), ('nicklas lidstrom',4)]

# sentiment_boxplot(coach_names, coach_wins, True)
# sentiment_boxplot(player_names, player_wins, False)

# coach_names = get_most_common_names(soup, 20, text_requirement=re.compile('coach'))
# player_names = get_most_common_names(soup, 20, text_requirement=re.compile('^((?!coach).)*$'))

# sentiment_histogram(player_names, coach_names)

# for name in coach_names + player_names:
# 	print(name)
# 	print(len(get_interviews_from(soup, name, all_together=False)))
# 	print()

# player_names = get_most_common_names(soup, 30, text_requirement=re.compile('^((?!coach).)*$'))
# words = get_all_words(soup, player_names)
# word_count = Counter(words)

# for word in word_count.most_common(500):
# 	print(word)

# coach_names = get_most_common_names(soup, 20, text_requirement=re.compile('coach'))
# player_names = get_most_common_names(soup, 20, text_requirement=re.compile('^((?!coach).)*$'))

# use Counter object soout of dictionary words will be mapped to 0
# selfish_lexicon = Counter({'i':1,'my':1,'i\'m':1,'i\'ve':1,'i\'ll':1,'myself':1,'we':-1,
# 				'our':-1,'us':-1,'we\'re':-1,'we\'ve':-1,'we\'ll':-1,'ourselves':-1})

# # selfish_boxplot(coach_names, selfish_lexicon, coach_wins, True)
# # selfish_boxplot(player_names, selfish_lexicon, player_wins, False)
# # selfishness_histogram(player_names, coach_names, selfish_lexicon)

coach_names = get_most_common_names(soup, 20, text_requirement=re.compile('coach'))
player_names = get_most_common_names(soup, 20, text_requirement=re.compile('^((?!coach).)*$'))
# scatter_selfishness_sentiment(coach_names, player_names, selfish_lexicon)
# log_odds_word_cloud(coach_names, player_names)

# word_cloud(coach_names, 'data/coach_mask.npy', 'coach_cloud.png')
# word_cloud(player_names, 'data/player_mask.npy', 'player_cloud.png')