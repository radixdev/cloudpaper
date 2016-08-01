import pickle

#handles the ids of submissions that have been replied to

print("starting id log open!")
FT_FILENAME = 'C:\Users\jrcontre\Dropbox\wallpaper changer\past_ids.txt'

FILENAME = FT_FILENAME
RAW_ID_FILE = open(FILENAME,'rb') 
print("id log loaded!")

if (len(RAW_ID_FILE.read())>0):
    ID_SET = pickle.load(open(FILENAME,"rb"))
    print("ID_LIST has ",len(ID_SET),"members")
else:
    ID_SET = set()
    
def saveIDs():
    #remember to call this when done!
    pickle.dump( ID_SET, open(FILENAME,'wb')  )
        
def isIdInList(id):
    return id in ID_SET
    
def addID(id):
    ID_SET.add(id) 
    saveIDs()
