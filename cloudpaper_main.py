import datetime

from downloader import WallPaperDownloader
from dropbox_uploader import DropboxUploader

if __name__ == '__main__':
    print '  '
    print '  '
    print datetime.datetime.now()

    WPD = WallPaperDownloader()
    WPD.run()

    DBU = DropboxUploader()
    DBU.run()

    print '  '
    print 'done'
    print datetime.datetime.now()
