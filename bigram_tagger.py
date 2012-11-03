import sys
import argparse
import math

# takes the parsed set of tags and the counts, and returns the set of tags with
# rare words replaced with _RARE_
def rarify(tags, wordCounts):
  for word in wordCounts:
    if wordCounts[word] < 5:
      for tag in tags:
        if word in tags[tag]:
          tags[tag]['_RARE_'] = 0 if '_RARE_' not in tags[tag] else tags[tag]['_RARE_']
          tags[tag]['_RARE_'] += int(tags[tag][word])
          del tags[tag][word]
    else:
      for tag in tags:
        if word in tags[tag]:
          wordMap[word] = [] if word not in wordMap else wordMap[word]
          wordMap[word].append(tag)
  return tags

# gives dictionary "tags" { tag: {word: count, word2: count2}, tag2: {word3: count3} }
def parseCounts(countsFile):
  tags = {}
  tagCounts = {}
  wordCounts = {}
  bigramStore = {}
  line = countsFile.readline()
  while line != '':
    parts = line.split()
    if parts[1] == "WORDTAG":
      count, rule, tag, word = parts
      count = int(count)
      
      wordCounts[word] = 0 if word not in wordCounts else wordCounts[word]
      wordCounts[word] += count
      
      tags[tag] = {} if tag not in tags else tags[tag]
      tags[tag][word] = 0 if word not in tags[tag] else tags[tag][word]
      tags[tag][word] += count
    if parts[1] == "1-GRAM":
      count, rule, tag = parts
      tagCounts[tag] = float(count)
    if parts[1] == "2-GRAM":
      count, rule, previous, tag = parts
      count = int(count)
      bigramStore[previous] = {} if previous not in bigramStore else bigramStore[previous]
      bigramStore[previous][tag] = count
    if parts[1] == "3-GRAM":
      pass
    line = countsFile.readline()
    
  tagCounts['*'] = sum(bigramStore['*'].values())
  tagCounts['STOP'] = tagCounts['*']
  return rarify(tags, wordCounts), tagCounts, bigramStore, wordCounts

# returns e(w|t)
def prob_given_tag(word, tag, tags, tagCounts, wordCounts):
  if word not in tags[tag]:
    
    # if this tag has no _RARE_ entry, force this word to be tagged something else
    if word == '_RARE_':
      return 0
    # if the word is in another tag, force it to be tagged as that tag
    elif word in wordMap and tag not in wordMap[word]:
      return 0
    else:
      return prob_given_tag('_RARE_', tag, tags, tagCounts, wordCounts)
  return float(tags[tag][word]) / tagCounts[tag]

# returns q(t_i | t_i-1)
def bigram_parameter(tag, previous, tagCounts, bigramStore):
  if tag not in bigramStore[previous]:
    return 0
  result = float(bigramStore[previous][tag]) / tagCounts[previous]
  return result

# grab the next sentence out of the block. It's a generator, thus iterable.
def nextSentence(f):
  sentence = []
  for line in f:
    if line != '\n':
      sentence.append(line.strip())
    else:
      result = list(sentence)
      sentence = []
      yield result

# do viterbi using the previous methods, and print the outcomes to stdout.
def viterbi(words, tags, tagCounts, wordCounts, bigramStore):
  backpointers = {}
  probabilities = {}
  word = words[0]
  for tag in tags:
    probabilities[(0, tag)] = bigram_parameter(tag, '*', tagCounts, bigramStore) * prob_given_tag(word, tag, tags, tagCounts, wordCounts)
  for i in xrange(1, len(words)):
    word = words[i]
    for tag in tags:
      options = []
      for previous in tags:
        options.append( (bigram_parameter(tag, previous, tagCounts, bigramStore) * prob_given_tag(word, tag, tags, tagCounts, wordCounts) * probabilities[(i-1, previous)], previous) )

      options.sort()
      prob, backpointer = options[-1]
      backpointers[(i, tag)] = backpointer
      probabilities[(i, tag)] = prob
  
  options = []
  for tag in tags:
    options.append( (probabilities[(len(words) - 1, tag)], tag) )
  options.sort()
  
  prob, tag = options[-1]
  
  results = [options[-1]]
  for i in xrange(len(words) - 1, 0, -1):
    previous = backpointers[(i, tag)]
    prob = probabilities[(i, tag)]
    results.append( (prob, previous) )
    tag = previous
  results.reverse()
  for i in xrange(len(words)):
    tag = results[i][1]
    prob = results[i][0]
    sys.stdout.write(words[i] + ' ' + tag + ' ' + str(math.log(prob, 2)) + '\n')
  sys.stdout.write('\n')
  return results

# run the viterbi on every sentence
def tag_all_words(inputFile, tags, tagCounts, bigramStore, wordCounts):
  for sentence in nextSentence(inputFile):
    viterbi(sentence, tags, tagCounts, bigramStore, wordCounts)

parser = argparse.ArgumentParser(description="NER engine.")
parser.add_argument("counts", help="the file containing tag counts")
parser.add_argument("input", help="the file with a test sample")
args = parser.parse_args()

wordMap = {}
countsFile = open(args.counts, 'r')
tags, tagCounts, bigramStore, wordCounts = parseCounts(countsFile)

inputFile = open(args.input, 'r')
tag_all_words(inputFile, tags, tagCounts, wordCounts, bigramStore)














