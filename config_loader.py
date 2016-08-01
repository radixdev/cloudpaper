import json

class ConfigLoader(object):
	def __init__(self):
		with open("cloudpaper-config.json") as data_file:
			self.config = json.load(data_file)

	def getDropboxAccessToken(self):
		return self.config['dropbox_access_token']

	def getImgurWaitSeconds(self):
		return self.config['imgur_api_wait_seconds']

	def getImgurClientIds(self):
		return self.config['imgur_api_client_ids']

	def getIsDebug(self):
		return self.config['debug']

	def getPruneEnabled(self):
		return self.config['prune_enabled']

	def getPruneAgeDays(self):
		return self.config['prune_max_age_days']

	def getWatchedSubreddits(self):
		return self.config['watched_subreddits']

	def getDownloaderMinVotes(self):
		return self.config['downloader_min_votes']

	def getMaxLogFileSizeMB(self):
		return self.config['max_log_file_size_mb']

	def getMaxTempFolderSizeMB(self):
		return self.config['max_temp_folder_size_mb']

	def getDropboxUploadEnabled(self):
		return self.config['upload_enabled']

	def getTargetScreenAspectRatio(self):
		return self.config["target_screen_width"] / self.config["target_screen_height"]

if __name__ == "__main__":
	C = ConfigLoader()
	print C.getDropboxAccessToken()
	print C.getImgurWaitSeconds()
	print C.getImgurClientIds()
	print C.getIsDebug()
	print C.getPruneEnabled()
	print C.getPruneAgeDays()
	print C.getWatchedSubreddits()
	print C.getDownloaderMinVotes()
	print C.getMaxLogFileSizeMB()
	print C.getMaxTempFolderSizeMB()
	print C.getDropboxUploadEnabled()
	print C.getTargetScreenAspectRatio()