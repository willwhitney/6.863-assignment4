inputFile = open('ner_dev.dat')


def get_next_line(f):
  for line in f:
    yield line
    
print get_next_line(inputFile).next()
print get_next_line(inputFile).next()
print get_next_line(inputFile).next()
print get_next_line(inputFile).next()
print get_next_line(inputFile).next()
print get_next_line(inputFile).next()