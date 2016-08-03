# cloudpaper
Wallpaper downloader from Reddit to dropbox

### To run

1. Create a `cloudpaper-config.json` in the same directory as the code.
    ```
    {
    	"debug":false,
    
    	"dropbox_access_token":"",
    
    	"prune_enabled":false,
    	"prune_max_age_days":128,
    	"upload_enabled":false,
    
    	"watched_subreddits":[ "MinimalWallpaper","wallpaperdump","wqhd_wallpaper","gamewalls"],
    
    	"imgur_api_client_ids":[],
    	"imgur_api_wait_seconds": 30,
    
    	"downloader_min_votes": 10,
    
    	"max_log_file_size_mb": 3,
    
    	"target_screen_width": 2556.0,
    	"target_screen_height": 1440.0,
    
    	"max_temp_folder_size_mb" : 900
    }
    ```
3. Attain a dropbox auth token and place it in the json config
4. Attain at least one imgur api key place it in the json config
3. Run the `cloudpaper_main.py` file or just run the bash script

### Misc
1. Add any number of subreddits as you want to the `watched_subreddits` key in the config.
2. The `imgur_api_client_ids` are cycled as not go over api request limits on any single key. Nonetheless, if you start running into "429 Client Error" from the imgur api, either set the `imgur_api_wait_seconds` to be higher, or just add more api keys.
3. The program uploads the wallpapers into a dropbox folder `/wallpaper changer/wallpapers/`.

### Advanced
Have the bash script run on a chronjob. I have a raspberry pi running this 24/7 every 6 hours.
