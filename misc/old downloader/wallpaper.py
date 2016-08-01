import praw		#reddit library
import urllib	#download files to local
import time		#lay dormant until it is time to refresh the images
import os		#do some system operations
import sys
import pyimgur
from random import randint
import id_logger as logger

#Program self-management
def restart_program():
    """Restarts the current program.
    Note: this function does not return. Any cleanup action (like
    saving data) must be done before calling this function."""
    python = sys.executable
    os.execl(python, python, * sys.argv)

def downloadUrl(url, extension, name=""):
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
  
def digTheImgurTree(url):
    print "digging"
    #do some more digging! dl the imgur links here if found
    isImgur = im.is_imgur_url(url)
    
    if (not isImgur):
        return (False, "")
        
    #get the imgur stuff
    time.sleep(5)
    obj = im.get_at_url(url)
    if (obj is None):
        return
        
    #determine is gallery
    if (hasattr(obj,"is_album") is False):
        isGallery = False
    else:   
        isGallery = obj.is_album
    
    #if obj is a gallery, then obj.images contains the image objects
    #if not, then obj ITSELF is an image!
    if (isGallery):
        for image in obj.images:
            link = image.link
            (isImage, fileType) = findTheImageType(link)
            #there's no name to give them
            downloadUrl(link, fileType, image.id)
    else:
        link = obj.link
        (isImage, fileType) = findTheImageType(link)
        downloadUrl(link, fileType, obj.id)
  
def findTheImageType(url):
    #retrieve the image type / gif (.png,.jpg)
    #returns (is valid image bool, type string)
   
    #get the file extension
    f = url.split(".")[-1]
    
    if (f == "jpg" or f == "jpeg" or f == "apng" or f == "png" or f == "bmp"):
        return (True, f )
    
    digTheImgurTree(url) #dl the links through this method
    return (False, "")

#constants and variables
user_agent = ("Wallpaper farmer by a person with no account :(") # for praw aquisition

FREQ = 18000 #how often to download a new set of images in seconds
NUM_IMAGES = 100 # number of images max 100

r = praw.Reddit(user_agent=user_agent)

#pyimgur data
CLIENT_ID = "eb8cd93defab332"
im = pyimgur.Imgur(CLIENT_ID)

def runWallpaperDownloader():
    print 'fresh start'
    submissions = r.get_subreddit('wallpaper+earthporn+skyporn+fireporn').get_top(limit=NUM_IMAGES)
    # iterate through the submissions and save local copies of the images to the '/images' directory
    if (submissions is not None):
        i=0
        for s in submissions:
            i+=1
            url = s.url
            (isImage, fileType) = findTheImageType(url)
            if (isImage):
                downloadUrl( url, fileType, s.id)
            
            # filename = directory+ s.id+ "." + "jpg"
            # urllib.urlretrieve(url, filename)#+ findTheImageType(s))
            # print url
            # if (i % 1):
                # time.sleep(1)
        print "done downloading"        
        time.sleep(FREQ) #pause operation so as to not constantly refresh images

while True:
    runWallpaperDownloader()