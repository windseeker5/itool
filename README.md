A Simple python tool to play with IPTV :tv: and re/streaming with nginx

# How to use it

1. git clone this repo
2. pip install -r requirements.txt
3. Edit or create a config.yml file with your service provider and where to store files and database

config.yml :
```yaml
  ---
  m3u_service: http://....../get.php?username=...&password=...&type=m3u_plus&output=ts
  m3u_file_fullsize: Fulliptv.m3u
  m3u_file_downsized: Small.m3u
  db_file: Fulliptv.db
```

4. Files and SQlite database are stored in folder iptv_dat/ created by this tool
   
