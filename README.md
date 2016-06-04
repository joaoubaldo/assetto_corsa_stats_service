# Assetto Corsa Stats Service

This project contains the following components:

- cron script: this is the script that reads and processes driver results and stores data in a sqlite db file.
- stats service: this is a wsgi service used to interact with the stored data

## Stats service
 Exposed paths:
   - */api/tracks*: returns a list of unique tracks stored in db
   - */api/tracks/{track_name}/bestlaps*: returns a list of all the best laps for a specific track.  
      Example: ```[..., {"car_name": "ferrari_458_gt2", "track_name": "monza", "driver_name": "FooBar", "best_lap": 426007}, ...]```
