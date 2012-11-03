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

superResistant= []
#for each virus
for virus in self.viruses:
   #check each drug in the drugResist list
   for drugs in drugResist:
       #if the virus is resistant to this drug...
       if virus.isResistantTo(drug):
           #and it is not already in the superResistant list...
           if virus not in superResistant:
               #add virus to the list
               superResistant.append(virus)
       #if the virus is not resistant to this drug..
       elif virus.isResistantTo(drug)== False:
           #and it is in the list...
           if virus in superResistant:
               #remove it from the list
               superResistant.remove(virus)
           else:
               #exit this loop and check another virus
               break

for virus in self.viruses:
  for drug in drugResist:
    if not virus.isResistantTo(drug):
      break
  superResistant.append(virus)
  