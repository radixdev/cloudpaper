# files ending with "keep" are not pruned from the wallpapers dropbox folder.

import time
from datetime import datetime
import os       #do some system operations
import sys #dump output to files
import shutil

import config_loader as ConfigLoader

import dropbox

CURRENT_DIRECTORY = os.path.dirname(os.path.abspath(sys.argv[0]))

# gets the age in days from today
# def calculateAge(born):
#     return (datetime.now() - born).days

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
        self.getAllWallpaperEntries()

        # Create a set of all the entry paths
        self.createEntryPathSet()

    def pruneWallpapers(self):
        if not self.shouldPrune:
            print "PRUNING OFF. RETURNING"
            return

        # Iterate over each entry and get its age
        entriesToDelete = []
        for entry in self.allEntries:
            # is the file old enough?
            fileAgeInDays = (datetime.now() - entry.server_modified).days
            isFileTooOld = fileAgeInDays > self.config.getPruneAgeDays()

            # can we even delete this file?
            isFilenameTemporary = not ("_keep" in entry.name)

            if (isFileTooOld and isFilenameTemporary):
                print 'marking file for batch deletion', fileAgeInDays, filePath
                entriesToDelete.append(entry)

        # pass the marked entries for batch deletion
        if (len(entriesToDelete) > 0):
            print "not actually batch deleting files just yet!"
            # self.client.files_delete_batch(entriesToDelete)

    # record all the existing wallpaper paths, continuing via cursor if needed
    def getAllWallpaperEntries(self):
        entries = []
        folderResult = self.client.files_list_folder("/wallpaper changer/wallpapers")

        if (folderResult is None):
            print "folder result was null"
            return entries

        shouldContinue = True
        while (shouldContinue):
            for entry in folderResult.entries:
                entries.append(entry)

            # determine if we continue or not
            shouldContinue = folderResult.has_more
            if (shouldContinue):
                # continue on cursor for the next loop
                folderResult = self.client.files_list_folder_continue(folderResult.cursor)

        self.allEntries = entries

    def createEntryPathSet(self):
        pathSet = set()
        for entry in self.allEntries:
            pathSet.add(entry.name)

        self.entryPathSet = pathSet

    def doesFileExistInWallpapers(self, filename):
        return filename in self.entryPathSet

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
            print("deleting file at path " + fileFullPath)
            if self.shouldUpload:
                os.remove(fileFullPath)

        # delete old files
        self.pruneWallpapers()

        # housekeeping
        self.maintainSizesOfLogFiles()

if __name__ == '__main__':
    DBU = DropboxUploader()
    DBU.setupDropboxAPI()
    DBU.pruneWallpapers()
    # DBU.run()
