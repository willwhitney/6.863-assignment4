import sys
import argparse
import math

def rarify(tags, wordCounts):
  for word in wordCounts:
    if wordCounts[word] < 5:
      for tag in tags:
        if word in tags[tag]:
          temp = tags[tag][word]
          del tags[tag][word]
          tags[tag]['_RARE_'] = 0 if '_RARE_' not in tags[tag] else tags[tag]['_RARE_']
          tags[tag]['_RARE_'] += temp

# dictionary "tags" { tag: {word: count, word2: count2}, tag2: {word3: count3} }
def parseCounts(countsFile):
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
      pass
    if parts[1] == "3-GRAM":
      pass
    line = countsFile.readline()
  return rarify(tags, wordCounts), tagCounts, bigramStore

def prob_given_tag(word, tag):
  return float(tags[tag][word]) / tagCounts[tag]
  
def optimal_word_tagging(tags, word):
  probs = []
  for tag in tags:
    if word in tags[tag]:
      probs.append( (prob_given_tag(word, tag), tag) )
  if len(probs) == 0:
    return optimal_word_tagging(tags, "_RARE_")
  else:
    probs.sort()
    return word, probs[-1][1], math.log(probs[-1][0], 2)

def tag_all_words(tags, inputFile):
  for word in inputFile:
    if len(word.strip()) == 0:
      sys.stdout.write('\n')
      continue
    word = word.rstrip('\n')
    usedWord, tag, logProb = optimal_word_tagging(tags, word)
    sys.stdout.write(word + ' ' + tag + ' ' + str(logProb) + '\n')

parser = argparse.ArgumentParser(description="NER engine.")
parser.add_argument("counts", help="the file containing tag counts")
parser.add_argument("input", help="the file with a training sample")
args = parser.parse_args()

# dictionary "tags" { tag: {word: count, word2: count2}, tag2: {word3: count3} }
tags = {}
tagCounts = {}

countsFile = open(args.counts, 'r')
parseCounts(countsFile)

inputFile = open(args.input, 'r')
tag_all_words(tags, inputFile)

