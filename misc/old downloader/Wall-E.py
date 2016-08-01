import praw		#reddit library
import urllib	#download files to local
import time		#lay dormant until it is time to refresh the images
import os		#do some system operations
import sys
import pyimgur
import traceback #get the stack trace for caught exceptions
from random import randint
import id_logger as logger

def restart_program():
    """Restarts the current program.
    Note: this function does not return. Any cleanup action (like
    saving data) must be done before calling this function."""
    python = sys.executable
    os.execl(python, python, * sys.argv)
    
def getFileTypeFromLink(url):
    #manually get the file extension, bit riskier!
    f = url.split(".")[-1]
    if (f == "jpg" or f == "jpeg" or f == "apng" or f == "png" or f == "bmp"):
        return f
    else:
        return ""
    
class WallPaperDownloader(object):
    def __init__(self):
        self.live= True
        self.r = praw.Reddit(user_agent='subreddit wallpaper downloader /u/radixdev')
        # self.numImagesToTry = 1000 #100 is the max anyway

        #pyimgur data
        # CLIENT_ID = "eb8cd93defab332"
        # self.im = pyimgur.Imgur(CLIENT_ID)
        IMGUR_CLIENT_ID_LIST = ["eb8cd93defab332",  "d5a9c4ff17a7363", "0e80b0aee14f6c1", "4ab59796d43f65e", "3c43b1035b58fab"]
        
        #prepare the handlers in advance
        self.imgurHandlerList = []
        for clientIDString in IMGUR_CLIENT_ID_LIST:
            handler = pyimgur.Imgur( clientIDString )
            self.imgurHandlerList.append( handler )
            
        self.imgurID_index = 0
        
        #subreddits to scan for wallpapers
        # self.subreddits = "spaceporn+waterporn+destructionporn+geekporn+botanicalporn+designporn+skyporn+fireporn+wallpapers"
        self.subredditList = ["imaginarylandscapes","spaceporn","waterporn","geekporn","botanicalporn","designporn","skyporn","fireporn","wallpapers","gamewalls"]
        
    def downloadUrl(self, url, extension, name):
        if not self.live: 
            print 'DL!! ',url, extension, name
            return

        if extension == "":
            return
            
        directory = "C:/Users/jrcontre/Dropbox/wallpaper changer/wallpapers/"
        if name is "":
            print "no name!"
            name = str(randint(1,65536))
            
        if not logger.isIdInList(name):   
            logger.addID(name)           
            urllib.urlretrieve(url, directory + name + "." + extension)
                
            print "download sucessful", url, extension, name 
        else:
            print("already downloaded image "+url+" with filename "+name+ "."+extension)
   
    def getImgurAPIhandler(self):
        #cycle through the api keys to hack the api timeouts, returns imgur handler
        
        #get the handler we're gonna return
        imgur_handler = self.imgurHandlerList[self.imgurID_index]
        
        #increment the index
        self.imgurID_index = (self.imgurID_index +1) % len(self.imgurHandlerList)
        
        return imgur_handler
        
    def isGoodImgurImage(self, imgurImage):
        #must have good dimensions
        myScreen = 1920/1080
        goodDim = abs( imgurImage.width / imgurImage.height - myScreen ) < 0.05
        
        #must be horizontal
        isHorizontal = (imgurImage.width >= imgurImage.height)
        
        #must be high res
        isHighRes = imgurImage.width > 1600
        
        print 'w x h', imgurImage.width, imgurImage.height 
        print 'goodDim',goodDim,'isHorizontal',isHorizontal, 'isHighRes', isHighRes
        
        return (goodDim and isHorizontal and isHighRes)
        
    def handleUrl(self, url, subName):
        #returns whether we handled the url or not
        
        #imgur vs not
        if "imgur.com" in url:
            # print 'waiting'
            time.sleep(5) #this has to break
            
            #is imgur, check for pic, gif, or album
            imgur_object = self.getImgurAPIhandler().get_at_url(url)
            
            imageTypeName = type(imgur_object).__name__.lower()
            
            #album, gallery or otherwise
            if ("album" in imageTypeName):
                for image in imgur_object.images:
                    print 'going through the rabbit hole'
                    
                    self.handleUrl(image.link,subName)
                    
                return True
 
            #image, gallery or otherwise
            if ("image" in imageTypeName):
                #gif or image?
                if (not imgur_object.is_animated):
                    #is an image!
                    if not self.isGoodImgurImage(imgur_object): 
                        print 'bad'
                        return False
                    
                    # extension = imgur_object.type.split("/")[1] #get the 'png' from 'image/png'
                    extension = getFileTypeFromLink(url)
                    self.downloadUrl(url, extension, imgur_object.id+"_"+subName)
                    return True
                    
        else:
            #fuck non imgur links
            return False
            
            # #manually get the file extension, bit riskier!
            # f = url.split(".")[-1]
            
            # if (f == "jpg" or f == "jpeg" or f == "apng" or f == "png" or f == "bmp"):
                # self.downloadUrl(url, f, "")
                # return True
                
        return False
        
    def run(self):
        #get submissions
        #download!
        
        for subreddit in self.subredditList:
            print 'on subreddit %r' % subreddit
            print ' '
            print ' '
            # submissions = self.r.get_subreddit(self.subreddits).get_top(limit=self.numImagesToTry)
            submissions = self.r.get_subreddit(subreddit).get_top(limit=100)
            
            for s in submissions:
                url = s.url
                self.handleUrl(url,s.subreddit.__str__())
            
if __name__ == '__main__':
    WPD = WallPaperDownloader()
    
    try:   
        while True:
            try:
                WPD.run()
                print "waiting until next execution"
                time.sleep(3600 *1.5) #wait
            except Exception, e_:
                print 'python is hard'
                time.sleep(60*10)
                
    except Exception, e:   
        ex = traceback.format_exc()
        # sendLogEmail("reuse parser has crashed. restarting.  \n"+e.message+"\n"+ex)
        
        print "caught exception",e.message
        print ex
        time.sleep(10) #give it some time to restart
        restart_program()