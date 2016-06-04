# Assetto Corsa Stats Service

This project contains the following components:

- cron script: this is the script that reads and processes driver results and stores data in a sqlite db file.
- stats service: this is a wsgi service used to interact with the stored data

## Stats service
 Exposed paths:
   - */api/tracks*: returns a list of unique tracks stored in db
   - */api/tracks/{track_name}/bestlaps*: returns a list of all the best laps for a specific track.  
      Example: ```[..., {"car_name": "ferrari_458_gt2", "track_name": "monza", "driver_name": "FooBar", "best_lap": 426007}, ...]```

## Installation

 pip install -r requirements.txt (virtualenv is recommended)

### Example crontab job
```*/2 * * * * /opt/assetto_stats_service/assetto_stats_cron.py /path/to/assetto_corsa/dedicated/server/results /opt/assetto_stats_service/assetto_stats.db```

### Example supervisord service configuration:
```
 [program:assetto_corsa_stats]
 command=/opt/assetto_stats_service/python27/bin/python assetto_stats_service.py
 directory=/opt/assetto_stats_service
 numprocs=1
 user=nobody
```
