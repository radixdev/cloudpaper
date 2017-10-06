# files ending with "keep" are not pruned from the wallpapers dropbox folder.

import time, datetime
import os       #do some system operations
import sys #dump output to files
import shutil

import config_loader as ConfigLoader

import dropbox

CURRENT_DIRECTORY = os.path.dirname(os.path.abspath(sys.argv[0]))

def getFileAgeInDaysFromMetadata(timeString):
    # remove the +0000 from the end of the string since %z isn't always supported
    mTime = timeString[0:-6]
    timestamp = time.mktime(datetime.datetime.strptime(mTime, "%a, %d %b %Y %H:%M:%S").timetuple())
    mTimeSecondsDelta = (time.time()-timestamp)
    mTimeDaysDelta = mTimeSecondsDelta / 82800
    # print mTimeDaysDelta
    return mTimeDaysDelta

class DropboxUploader(object):
    def __init__(self):
        self.config = ConfigLoader.ConfigLoader()
        self.DOWNLOAD_DIRECTORY = os.path.join(CURRENT_DIRECTORY, "tmp")
        self.shouldPrune = self.config.getPruneEnabled()
        self.shouldUpload = self.config.getDropboxUploadEnabled()

    # make sure the log files don't get out of hand
    def maintainSizesOfLogFiles(self):
        filesInThisFolder = os.listdir(CURRENT_DIRECTORY)

        for filename in filesInThisFolder:
            fileFullPath = os.path.join(CURRENT_DIRECTORY, filename)

            if (filename.lower().startswith("cloudpaper_log") or filename.lower().startswith("past_ids")):
                if (filename.lower().endswith("._backup")):
                    # don't just make backups forever lol
                    continue

                # if larger than maxLogSize, then create a backup copy
                isFileTooLarge = os.path.getsize(fileFullPath) / 1e6 > self.config.getMaxLogFileSizeMB()

                if (isFileTooLarge):
                    # move the file to a backup
                    print "moved file %s to backup file since it has size %i" % (filename, os.path.getsize(fileFullPath))
                    shutil.move(fileFullPath, os.path.join(CURRENT_DIRECTORY, filename + "._backup"))

    # TODO: one day this will all fail. Getting this to work will fix it
    def setupDropboxAPI(self):
        access_token = self.config.getDropboxAccessToken()
        print "getting client"
        self.client = dropbox.Dropbox(access_token)
        # self.folderMetadata = self.client.files_get_metadata("/wallpaper changer/wallpapers")
        # print(self.folderMetadata)
        # self.allFolderContentPaths = self.getAllWallpaperPaths()

        folderResult = self.client.files_list_folder("/wallpaper changer/wallpapers")
        print(folderResult.has_more)
        self.getAllWallpaperEntries()

    def pruneWallpapers(self):
        if not self.shouldPrune:
            print "PRUNING OFF. RETURNING"
            return

        folderContents = self.folderMetadata["contents"]

        for content in folderContents:
            if (not content["is_dir"]):
                # it's a file! client_mtime
                fileAgeInDays = getFileAgeInDaysFromMetadata(content["modified"])
                filePath = content["path"]

                isFileTooOld = fileAgeInDays > self.config.getPruneAgeDays()
                isFilenameTemporary = not ("_keep" in filePath)

                if (isFileTooOld and isFilenameTemporary):
                    print 'deleting file', fileAgeInDays, filePath
                    # delete!
                    try:
                        self.client.file_delete(filePath)
                    except Exception, e:
                        print e

    # record all the existing wallpaper paths, continuing via cursor if needed
    def getAllWallpaperEntries(self):
        paths = []
        folderResult = self.client.files_list_folder("/wallpaper changer/wallpapers")

        if (folderResult is None):
            print "fuck"
            return paths

        while (shouldContinue):
            for entry in folderResult.entries:
                print entry.path_lower
                paths.append(entry)

            # determine if we continue or not
            shouldContinue = folderResult.has_more
            if (shouldContinue):
                print("continuing on cursor")
                self.client.files_list_folder(folderResult.cursor)


        # get all the results and merge them all
        # print(folderResult.has_more)
        #
        # shouldContinue = true
        # while (shouldContinue):
        #     # get our entries
        #     for entry in folderResult:
        #         paths = paths + entry["path_lower"]
        #
        #     shouldContinue = folderResult.has_more
            # Get the next folder result




    # def getAllPathsFromFolderResult(self, result):


    def doesFileExistInWallpapers(self, filename):
        # As a safeguard, check if the file already exists!
        if (self.allFolderContentPaths is None):
            # some error happened, do a manual check
            print "running manual check for filename " + filename
            return self.runManualCheckOfFileExistence(filename)

        # how the file would appear in the metadata listing
        localFilename = "/wallpaper changer/wallpapers/" + filename
        # maybe presort this contents list?
        return localFilename in self.allFolderContentPaths

    # # directly makes an api call to see if the file already exists
    # def runManualCheckOfFileExistence(self, filename):
    #     try:
    #         fileMD = self.client.metadata("/wallpaper changer/wallpapers/" + filename)
    #         return True
    #     except dropbox.rest.ErrorResponse:
    #         print "Got dropbox.rest.ErrorResponse in doesFileExistInWallpapers for " + filename
    #         return False

    # # sets on this object every wallpaper path in the dropbox folder
    # # returns a list of strings of relative paths
    # def getAllWallpaperPaths(self):
    #     result = []
    #
    #     fileMD = self.folderMetadata
    #     folderContents = fileMD["contents"]
    #     if (folderContents is not None):
    #         for thing in folderContents:
    #             result.append(thing["path"])
    #
    #     return result

    def run(self):
        # find the files
        filesInTmpFolder = os.listdir(self.DOWNLOAD_DIRECTORY)

        if (len(filesInTmpFolder) < 3):
            print "Not enough files (%i present) in tmp folder for upload. Skipping for now" % len(filesInTmpFolder)
            return

        # we're good to go
        self.setupDropboxAPI()

        for filename in filesInTmpFolder:
            fileFullPath = os.path.join(self.DOWNLOAD_DIRECTORY, filename)
            print "preparing to upload", fileFullPath
            isFileDuplicate = self.doesFileExistInWallpapers(filename)

            if (isFileDuplicate):
                print "Not uploading file %r. Already exists in wallpapers directory!" % (fileFullPath)
            else:
                # upload the file
                f = open(fileFullPath, 'rb')
                if self.shouldUpload:
                    self.client.put_file('/wallpaper changer/wallpapers/' + filename, f)
                f.close()

            # delete the file
            os.remove(fileFullPath)

        # delete old files
        self.pruneWallpapers()

        # housekeeping
        self.maintainSizesOfLogFiles()

if __name__ == '__main__':
    DBU = DropboxUploader()
    DBU.setupDropboxAPI()
    # DBU.run()