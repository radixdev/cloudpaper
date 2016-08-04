import praw   #reddit library
import urllib   #download files to local
import urllib2
import time   #lay dormant until it is time to refresh the images
import os   #do some system operations
import sys
import pyimgur
from random import randint
import random
import id_logger as logger
import getimageinfo as getimageinfo
import config_loader as ConfigLoader

# see http://stackoverflow.com/a/9051055
CURRENT_DIRECTORY = os.path.dirname(os.path.abspath(sys.argv[0]))

# shitty hash code function
def stringHashcode(s):
  code = 1
  for i in s:
    code = code*31 + ord(i) & 0xFFFFF
  return str(code)

def get_size_mb(start_path):
  total_size = 0
  for dirpath, dirnames, filenames in os.walk(start_path):
      for f in filenames:
          fp = os.path.join(dirpath, f)
          total_size += os.path.getsize(fp)
  return total_size/1e6

class Stopwatch(object):
  def __init__(self, name):
    self.name = name
    self.startTime = 0
    self.endTime = 0

  def getTime(self):
    # 1e6 microseconds
    return (time.clock() * 1e6)

  def start(self):
    self.startTime = self.getTime()

  def end(self):
    self.endTime = self.getTime()

    #also print the shit
    elapsed = (self.endTime - self.startTime)
    print "%i microseconds elapsed for %s\n" % (elapsed, self.name)

class WallPaperDownloader(object):

  def __init__(self):
    self.config = ConfigLoader.ConfigLoader()

    if (self.config.getIsDebug()):
      print "running on debug values now. god help us all"
      self.IMGUR_WAIT_SECONDS = 0
      # self.downloadFiles = False
    else:
      self.IMGUR_WAIT_SECONDS = self.config.getImgurWaitSeconds()
      # self.downloadFiles = True

    self.r = praw.Reddit(user_agent='subreddit wallpaper downloader /u/call_me_miguel')

    #pyimgur data
    IMGUR_CLIENT_ID_LIST = self.config.getImgurClientIds()

    # distribute the load
    random.shuffle(IMGUR_CLIENT_ID_LIST)

    #prepare the handlers in advance
    self.imgurHandlerList = []
    for clientIDString in IMGUR_CLIENT_ID_LIST:
      handler = pyimgur.Imgur(clientIDString)
      self.imgurHandlerList.append(handler)
      
    self.imgurID_index = 0
    
    #subreddits to scan for wallpapers
    self.subredditList = self.config.getWatchedSubreddits()

    # some constants
    self.myScreen = self.config.getTargetScreenAspectRatio()
    self.DOWNLOAD_DIRECTORY = os.path.join(CURRENT_DIRECTORY, "tmp")

    # make the download directory
    if not os.path.exists(self.DOWNLOAD_DIRECTORY):
      os.makedirs(self.DOWNLOAD_DIRECTORY)

  def downloadUrl(self, url, extension, name):
    if extension == "":
      return
      
    if name is "":
      print "no name for file! random one given"
      name = str(randint(1,65536)) + url
      
    if not logger.isIdInList(url):   
      logger.addID(url)
      downloadPath = os.path.join(self.DOWNLOAD_DIRECTORY, name + "." + extension)   
      # params are used to fool user-agent checks (like i.reddit using Cloudflare)  
      # see http://stackoverflow.com/questions/2364593/urlretrieve-and-user-agent-python
      urllib.URLopener.version = 'Mozilla/5.0 (Windows NT 6.1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/35.0.1916.153 Safari/537.36 SE 2.X MetaSr 1.0'
      urllib.urlretrieve(url, downloadPath)
      
      print "download sucessful", url, extension, name, downloadPath
    else:
      print("already downloaded image "+url+" with filename "+name+ "."+extension)

  def getFileTypeFromLink(self, url):
    #manually get the file extension, bit riskier!
    f = url.split(".")[-1]
    if (f == "jpg" or f == "jpeg" or f == "apng" or f == "png" or f == "bmp"):
      return f
    else:
      return ""

  def getImgurAPIhandler(self):
    #cycle through the api keys to hack the api timeouts, returns imgur handler
    
    #get the handler we're gonna return
    imgur_handler = self.imgurHandlerList[self.imgurID_index]
    
    #increment the index
    self.imgurID_index = (self.imgurID_index + 1) % len(self.imgurHandlerList)
    
    return imgur_handler

  def isGoodImage(self,link, width, height):
    #must have good dimensions
    imageAspectRatioFloat = float(width) / float(height)
    goodDim = abs( imageAspectRatioFloat - self.myScreen ) < 0.05
    
    #must be horizontal
    isHorizontal = (width >= height)
    
    #must be high res
    isHighRes = width > 1800

    usingThisImage = (goodDim and isHorizontal and isHighRes)
    imageInfoFormatArgs = (usingThisImage, str(link), width, height, goodDim, isHorizontal, isHighRes)
    print "(%r) || link=%s || w=%i h=%i || goodDim=%r isHorizontal=%r isHighRes=%r" % imageInfoFormatArgs
    
    return usingThisImage
  
  def handleUrl(self, url, subName, redditId, albumName=""):
    #returns whether we handled the url or not
    
    #imgur vs not
    if "imgur.com" in url:
      time.sleep(self.IMGUR_WAIT_SECONDS)
      
      #is imgur, check for pic, gif, or album
      imgur_object = None
      try:
        imgur_object = self.getImgurAPIhandler().get_at_url(url)
      except Exception as e:
        print e
        return
      
      imageTypeName = type(imgur_object).__name__.lower()
      
      #album, gallery or otherwise
      if ("album" in imageTypeName):
        print 'going through the rabbit hole with length:', len(imgur_object.images)

        for image in imgur_object.images:
          if (self.isDownloadFolderTooLarge()):
            print "Early exiting large imgur album download. album: " + url
            # To retry downloading the album later, remove it from the set of stored ids
            # If it's still popular, the download will re-commence later
            # Super sloppy way of doing it (should hard save the id somewhere) but fuck it
            id_logger.remove(redditId)
            break

          self.handleUrl(image.link, subName, redditId, albumName=imgur_object.id)
          
        return True
   
      #image, gallery or otherwise
      if ("image" in imageTypeName):
        #gif or image?
        if (not imgur_object.is_animated):
          #is an image!
          if not self.isGoodImage(imgur_object.link, imgur_object.width, imgur_object.height):
            return False
          
          extension = self.getFileTypeFromLink(url)
          imageFilename = imgur_object.id + "_"+subName

          if (albumName != ""):
            # there's an album to prefix it with
            imageFilename = "__" + albumName + "__" + imageFilename

          # print imageFilename, albumName
          self.downloadUrl(url, extension, imageFilename)
        return True
        
    else:
      # fuck non imgur links... no longer!
      # Do a partial download of the file to glean the resolution
      (image_type, width, height) = self.getNonImgurImageInfo(url)
      if (image_type != None and image_type != "gif"):
        if not self.isGoodImage(url, width, height):
          return False

        # the filename should consist of the url (unique) and sub name
        imageFilename = "%s_%s_ni_%s" % (redditId, stringHashcode(url), subName)
        self.downloadUrl(url, image_type, imageFilename)
        return True
      else:
        # Nothing we can do
        print "skipping on url:" + url
        return False
      
    return False

  # Returns a tuple of (image_type, width, height)
  def getNonImgurImageInfo(self, url):
    try:
      hdr = {'User-Agent': 'Mozilla/5.0'}
      req = urllib2.Request(url,headers=hdr)
      imgdata = urllib2.urlopen(req)
      image_type,width,height = getimageinfo.getImageInfo(imgdata)
      return (image_type,width,height)
    except Exception,e:
      print e
      return (None, -1, -1)
  
  # return true if the folder is already too large
  def isDownloadFolderTooLarge(self):
    return (get_size_mb(self.DOWNLOAD_DIRECTORY) > self.config.getMaxTempFolderSizeMB())

  def run(self):
    #get submissions
    #download!
    for subreddit in self.subredditList:
      submissions = self.r.get_subreddit(subreddit).get_hot(limit=100)

      for s in submissions:
        if (self.isDownloadFolderTooLarge()):
          print "download folder was too large! Breaking to uploader"
          logger.saveIDs()
          return

        if not logger.isIdInList(s.id): 
          print "subreddit %s and post id %s" % (subreddit, s.id)
          logger.addID(s.id)

          # no shitty submissions
          if (s.score > self.config.getDownloaderMinVotes()):
            self.handleUrl(s.url, s.subreddit.__str__(), s.id)
          else:
            if (self.config.getIsDebug()):
              print "post skipped due to low upvote count"
      logger.saveIDs()

if __name__ == '__main__':
  print "testing the code itself"
  W = WallPaperDownloader()
  W.run()
