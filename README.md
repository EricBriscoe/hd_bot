# Horrible Subs to Deluge Bot
## Summary
Before running app.py make sure you set up the set_config function correctly.
Running app.py requires the selenium chromedriver which will be used to gather magnet links. 
You also must have the webui enabled in Deluge.
Do not mix the episodes with anime from other sources, create a separate folder for this app.
Once everything is configured run it and it should download all missing episodes.
If it fails to find episodes which are available, try extending the wait_time in get_magnet_links.