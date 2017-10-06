import pickle
import sys, os

# shitty hash code function
def stringHashcode(s):
  code = 1
  for i in s:
    code = code*31 + ord(i) & 0xFFFFF
  return code

#handles the ids of submissions that have been replied to
#make the filename unique so the linux and windows filenames are different
curDir = os.path.dirname(os.path.abspath(sys.argv[0]))
filename = 'past_ids_%i.txt' % stringHashcode(curDir) 
idFileAbsolutePath = os.path.join(curDir, filename)

# touch the file if not already here
if not os.path.isfile(idFileAbsolutePath):
    open(idFileAbsolutePath, 'a').close()

RAW_ID_FILE = open(idFileAbsolutePath, "rb")
rawContents = RAW_ID_FILE.read()

if (len(rawContents) > 0):
    try:
        ID_SET = pickle.loads(rawContents)
    except:
        ID_SET = set()
else:
    ID_SET = set()

def saveIDs():
    #remember to call this when done!
    f = open(idFileAbsolutePath, "wb")
    pickle.dump(ID_SET, f)
    f.close()
        
def isIdInList(id):
    return id in ID_SET

def removeID(id):
    if (isIdInList(id)):
        ID_SET.remove(id)
    
def addID(id):
    ID_SET.add(id) 
    # saveIDs()

# clears all the entries
def flush():
	print "set flushed!"
	ID_SET.clear()
	saveIDs()
