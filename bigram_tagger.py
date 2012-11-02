import sys
import argparse
import math

def rarify(tags, wordCounts):
  # print wordCounts
  # exit(0)
  for word in wordCounts:
    if wordCounts[word] < 5:
      for tag in tags:
        if word in tags[tag]:
          tags[tag]['_RARE_'] = 0 if '_RARE_' not in tags[tag] else tags[tag]['_RARE_']
          tags[tag]['_RARE_'] += int(tags[tag][word])
          # print "DELETING: ", tag, ':', word, ':', tags[tag][word]
          del tags[tag][word]
    else:
      for tag in tags:
        if word in tags[tag]:
          wordMap[word] = [] if word not in wordMap else wordMap[word]
          wordMap[word].append(tag)
  # print tags
  # for tag in tags:
  #   try:
  #     print tags[tag]['_RARE_']
  #   except KeyError:
  #     print "ERROR: ", tag
  # exit(0)
  # print tags
  # print wordMap
  return tags

# dictionary "tags" { tag: {word: count, word2: count2}, tag2: {word3: count3} }
def parseCounts(countsFile):
  # sys.stdout.write('parseCounts')
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
    
  # print bigramStore
  tagCounts['*'] = sum(bigramStore['*'].values())
  tagCounts['STOP'] = tagCounts['*']
  return rarify(tags, wordCounts), tagCounts, bigramStore, wordCounts

def prob_given_tag(word, tag, tags, tagCounts, wordCounts):
  # print word
  if word not in tags[tag]:
    # print "Word ", word, " not found in tag ", tag
    # if word in wordCounts and wordCounts[word] > 5:
    #   return 0
    if word == '_RARE_':
      # print "Word is RARE with probability 0 in prob_given_tag"
      return 0
    elif word in wordMap and tag not in wordMap[word]:
      # print "Word ", word, " is NOT RARE. Recycling..."
      return 0
    else:
      # print "Word ", word, " is RARE in prob_given_tag for tag ", tag
      return prob_given_tag('_RARE_', tag, tags, tagCounts, wordCounts)
  # print "prob of ", word, " given tag ", tag, " is ", float(tags[tag][word]) / tagCounts[tag]
  return float(tags[tag][word]) / tagCounts[tag]

def bigram_parameter(tag, previous, tagCounts, bigramStore):
  # print tagCounts[previous]
  # print store[previous]
  if tag not in bigramStore[previous]:
    # print "TA`ramStore
    return 0 #1 / tagCounts[previous]
  result = float(bigramStore[previous][tag]) / tagCounts[previous]
  return result

def nextSentence(f):
  sentence = []
  for line in f:
    if line != '\n':
      sentence.append(line.strip())
    else:
      result = list(sentence)
      sentence = []
      yield result


def viterbi(words, tags, tagCounts, wordCounts, bigramStore):
  backpointers = {}
  probabilities = {}
  # print words
  word = words[0]
  # if word == "May":
  #   print '--------------------------------------------------------'
  for tag in tags:
    # if word == "May":
      # print bigram_parameter(tag, '*', tagCounts, bigramStore)
    probabilities[(0, tag)] = bigram_parameter(tag, '*', tagCounts, bigramStore) * prob_given_tag(word, tag, tags, tagCounts, wordCounts)
  # print probabilities
    # if word == "May":
      # print probabilities
  # exit()
  for i in xrange(1, len(words)):
    word = words[i]
    for tag in tags:
      options = []
      for previous in tags:
        # print previous, tag, bigram_parameter(tag, previous, tagCounts, bigramStore) * prob_given_tag(word, tag, tags, tagCounts, wordCounts) * probabilities[(i-1, previous)]
        options.append( (bigram_parameter(tag, previous, tagCounts, bigramStore) * prob_given_tag(word, tag, tags, tagCounts, wordCounts) * probabilities[(i-1, previous)], previous) )
      options.sort()
      # print options
      prob, backpointer = options[-1]
      backpointers[(i, tag)] = backpointer
      probabilities[(i, tag)] = prob
    # print backpointers
    # print probabilities
    # exit(0)
    
  
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
  # print results
  # exit()
  for i in xrange(len(words)):
    tag = results[i][1]
    prob = results[i][0]
    # print tag, prob
    # try:
    sys.stdout.write(words[i] + ' ' + tag + ' ' + str(math.log(prob, 2)) + '\n')
    # except ValueError:
      # print words
      # print probabilities
      # print results
      # exit(0)
  sys.stdout.write('\n')
  # exit(0)
  return results
  
      
    
        
        
        
        
      # max([bigram_parameter(tag, previous, tagCounts, bigramStore) * prob_given_tag(word, tag) for previous in tags])
      
  

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
# print wordCounts

# print tags
# print tags, tagCounts, bigramStore

inputFile = open(args.input, 'r')
tag_all_words(inputFile, tags, tagCounts, wordCounts, bigramStore)














