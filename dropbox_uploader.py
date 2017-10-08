# files ending with "keep" are not pruned from the wallpapers dropbox folder.

import time
from datetime import datetime
import os
import sys
import shutil

import dropbox

import config_loader as ConfigLoader

CURRENT_DIRECTORY = os.path.dirname(os.path.abspath(sys.argv[0]))

class DropboxUploader(object):
    def __init__(self):
        self.config = ConfigLoader.ConfigLoader()
        self.DOWNLOAD_DIRECTORY = os.path.join(CURRENT_DIRECTORY, "tmp")
        self.shouldPrune = self.config.getPruneEnabled()
        self.shouldUpload = self.config.getDropboxUploadEnabled()
        self.setupDropboxAPI()

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

    def setupDropboxAPI(self):
        access_token = self.config.getDropboxAccessToken()
        print "getting client"
        self.client = dropbox.Dropbox(access_token)
        self.getAllWallpaperEntries()

        # Create a set of all the entry paths
        self.createEntryPathSet()

    def deleteDuplicateWallpapers(self):
        hashes = {}
        entriesToDelete = []
        for entry in self.allEntries:
            h = entry.content_hash
            if h in hashes:
                print("Duplicate file " + entry.path_lower + " matches " + hashes[h])
                entriesToDelete.append(dropbox.files.DeleteArg(entry.path_lower))
            else:
                hashes[h] = entry.path_lower

        # pass the marked entries for batch deletion
        if (len(entriesToDelete) > 0):
            print "batch deleting %r duplicate files" % (len(entriesToDelete))
            self.client.files_delete_batch(entriesToDelete)

    def pruneWallpapers(self):
        if not self.shouldPrune:
            print "PRUNING OFF. RETURNING"
            return

        # Iterate over each entry and get its age
        # This is a list of DeleteArg objects
        entriesToDelete = []
        for entry in self.allEntries:
            # is the file old enough?
            fileAgeInDays = (datetime.now() - entry.server_modified).days
            isFileTooOld = fileAgeInDays > self.config.getPruneAgeDays()

            # can we even delete this file?
            isFilenameTemporary = not ("_keep" in entry.name)

            if (isFileTooOld and isFilenameTemporary):
                print 'marking file for batch deletion', fileAgeInDays, entry.name
                entriesToDelete.append(dropbox.files.DeleteArg(entry.path_lower))

        # pass the marked entries for batch deletion
        if (len(entriesToDelete) > 0):
            print "batch deleting %r files" % (len(entriesToDelete))
            self.client.files_delete_batch(entriesToDelete)

    # record all the existing wallpaper paths, continuing via cursor if needed
    def getAllWallpaperEntries(self):
        entries = []
        folderResult = self.client.files_list_folder("/wallpaper changer/wallpapers", include_deleted=False)

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

    def uploadFiles(self):
        # find the files
        filesInTmpFolder = os.listdir(self.DOWNLOAD_DIRECTORY)

        if (len(filesInTmpFolder) < 3):
            print "Not enough files (%i present) in tmp folder for upload. Skipping for now" % len(filesInTmpFolder)
            return

        for filename in filesInTmpFolder:
            fileFullPath = os.path.join(self.DOWNLOAD_DIRECTORY, filename)
            print "preparing to upload", fileFullPath
            isFileDuplicate = self.doesFileExistInWallpapers(filename)

            if (isFileDuplicate):
                print "Not uploading file %r. Already exists in wallpapers directory!" % (fileFullPath)
            else:
                # upload the file
                # see https://stackoverflow.com/a/33828537
                if self.shouldUpload:
                    with open(fileFullPath, 'rb') as f:
                        self.client.files_upload(f.read(), '/wallpaper changer/wallpapers/' + filename)

            # delete the file
            print("deleting file at path " + fileFullPath)
            if self.shouldUpload:
                os.remove(fileFullPath)

    def run(self):
        # I wonder what this method does
        self.uploadFiles()

        # delete old files
        self.pruneWallpapers()

        self.deleteDuplicateWallpapers()

        # housekeeping
        self.maintainSizesOfLogFiles()

if __name__ == '__main__':
    DBU = DropboxUploader()
    DBU.pruneWallpapers()
    DBU.deleteDuplicateWallpapers()
    # DBU.run()
