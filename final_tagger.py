import sys
import argparse
import math
import string


def isNumeric(word):
  for char in word:
    if char not in string.digits and char not in string.punctuation:
      return False
  return True
  
def substitute(word):
  sub = '_RARE_'
  if word[0] in string.uppercase:
    sub = '_CAP_'
  if word.upper() == word:
    sub = '_ALLCAPS_'
  if isNumeric(word):
    sub = '_NUM_'
  return sub

# takes the parsed set of tags and the counts, and returns the set of tags with
# rare words replaced with _RARE_
def rarify(tags, wordCounts):
  for word in wordCounts:
    if wordCounts[word] < 5:
      sub = substitute(word)
      for tag in tags:
        if word in tags[tag]:
          tags[tag][sub] = 0 if sub not in tags[tag] else tags[tag][sub]
          tags[tag][sub] += int(tags[tag][word])
          del tags[tag][word]
          wordMap[sub] = [] if sub not in wordMap else wordMap[sub]
          wordMap[sub].append(tag)
    else:
      for tag in tags:
        if word in tags[tag]:
          wordMap[word] = [] if word not in wordMap else wordMap[word]
          wordMap[word].append(tag)
  # exit()
  return tags

# gives dictionary "tags" { tag: {word: count, word2: count2}, tag2: {word3: count3} }
def parseCounts(countsFile):
  tags = {}
  tagCounts = {}
  wordCounts = {}
  trigramStore = {}
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
      pass
    if parts[1] == "3-GRAM":
      # print line
      count, rule, preprevious, previous, tag = parts
      count = int(count)
      trigramStore[(preprevious, previous)] = {} if (preprevious, previous) not in trigramStore else trigramStore[(preprevious, previous)]
      trigramStore[(preprevious, previous)][tag] = count
      bigramCounts[(preprevious, previous)] = 0 if (preprevious, previous) not in bigramCounts else bigramCounts[(preprevious, previous)]
      bigramCounts[(preprevious, previous)] += count
    line = countsFile.readline()
    
  tagCounts['*'] = sum(trigramStore[('*', '*')].values())
  tagCounts['STOP'] = tagCounts['*']
  return rarify(tags, wordCounts), tagCounts, trigramStore, wordCounts

# returns e(w|t)
def prob_given_tag(word, tag, tags, tagCounts, wordCounts):
  # if word == "May":
  #   print wordMap["May"]
  if word not in tags[tag]:
    
    # if this tag has no _RARE_ entry, force this word to be tagged something else
    # if word == '_RARE_':
    #   return 0
    # if the word is in another tag, force it to be tagged as that tag
    if word in wordMap and tag not in wordMap[word]:
      return 0
    else:
      if word in subs:
        if word != '_RARE_':
          return prob_given_tag('_RARE_', tag, tags, tagCounts, wordCounts)
        return 0
      return prob_given_tag(substitute(word), tag, tags, tagCounts, wordCounts)
    # else:
    #   if word == '_RARE_':
    #     return 0
    #   return prob_given_tag('_RARE_', tag, tags, tagCounts, wordCounts)
  return float(tags[tag][word]) / tagCounts[tag]

# returns q(t_i | t_i-1, t_i-2)
def trigram_parameter(tag, previous, preprevious, tagCounts, trigramStore):
  if (preprevious, previous) not in trigramStore:
    return 0
  if tag not in trigramStore[(preprevious, previous)]:
    return 0
  result = float(trigramStore[(preprevious, previous)][tag]) / bigramCounts[(preprevious, previous)]
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
def viterbi(words, tags, tagCounts, wordCounts, trigramStore):
  # print trigramStore
  backpointers = {}
  probabilities = {}
  word = words[0]
  
  # first word is a special case
  for tag in tags:
    try:
      tri = trigram_parameter(tag, '*', '*', tagCounts, trigramStore)
      given_tag = prob_given_tag(word, tag, tags, tagCounts, wordCounts)
      tri = -1000 if tri == 0 else math.log(tri, 2)
      given_tag = -1000 if given_tag == 0 else math.log(given_tag, 2)
      probabilities[(0, tag, '*')] = tri + given_tag
    except ValueError:
      print words
      print tag
      exit()
  
  # so is the second
  if len(words) > 1:
    word = words[1]
    for previous in tags:
      for tag in tags:
        tri = trigram_parameter(tag, previous, '*', tagCounts, trigramStore)
        given_tag = prob_given_tag(word, tag, tags, tagCounts, wordCounts)
        tri = -1000 if tri == 0 else math.log(tri, 2)
        given_tag = -1000 if given_tag == 0 else math.log(given_tag, 2)
        probabilities[(1, tag, previous)] = tri + given_tag + probabilities[(0, previous, '*')]
        backpointers[(1, tag, previous)] = '*'
  
  # work out the rest
  for i in xrange(2, len(words)):
    word = words[i]
    for tag in tags:
      for previous in tags:
        options = []
        for preprevious in tags:
          tri = trigram_parameter(tag, previous, preprevious, tagCounts, trigramStore)
          given_tag = prob_given_tag(word, tag, tags, tagCounts, wordCounts)
          tri = -1000 if tri == 0 else math.log(tri, 2)
          given_tag = -1000 if given_tag == 0 else math.log(given_tag, 2)
          prob = tri + given_tag + probabilities[(i - 1, previous, preprevious)]
          options.append( (prob, preprevious) )
        options.sort()
        prob, preprev = options[-1]
        probabilities[(i, tag, previous)] = prob
        backpointers[(i, tag, previous)] = preprev
  
  # pick the final end state
  options = []
  for tag in tags:
    if len(words) > 1:
      for prev in tags:
        options.append( (probabilities[(len(words) - 1, tag, prev)], (tag, prev)) )
    else:
      options.append( (probabilities[(len(words) - 1, tag, '*')], (tag, '*')) )
  options.sort()
  (prob, (tag, prev)) = options[-1]
  
  results = [(prob, (tag, prev))]
  
  # build up the results for this sentence
  for i in xrange(len(words) - 2, -1, -1):
    preprev = backpointers[(i+1, tag, prev)]
    tag = prev
    prev = preprev
    prob = probabilities[(i, tag, prev)]
    results.append( (prob, (tag, prev)) )
  results.reverse()
  
  # write them out
  for i in xrange(len(words)):
    (prob, (tag, prev)) = results[i]
    sys.stdout.write(words[i] + ' ' + tag + ' ' + str(prob) + '\n')
  sys.stdout.write('\n')
  return results
  
# run the viterbi on every sentence
def tag_all_words(inputFile, tags, tagCounts, trigramStore, wordCounts):
  for sentence in nextSentence(inputFile):
    viterbi(sentence, tags, tagCounts, trigramStore, wordCounts)

parser = argparse.ArgumentParser(description="NER engine.")
parser.add_argument("counts", help="the file containing tag counts")
parser.add_argument("input", help="the file with a test sample")
args = parser.parse_args()

subs = {'_RARE_', '_CAP_', '_ALLCAPS_', '_NUM_'}
wordMap = {}
bigramCounts = {}
countsFile = open(args.counts, 'r')
tags, tagCounts, trigramStore, wordCounts = parseCounts(countsFile)

inputFile = open(args.input, 'r')
tag_all_words(inputFile, tags, tagCounts, wordCounts, trigramStore)














