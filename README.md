# Assetto Corsa Stats Service

This project contains the following components:

- cron script: this is the script that reads and processes driver results and stores data in a sqlite db file.
- stats service: this is a wsgi service used to interact with the stored data and the minimal http interface AC provides

## Stats service
 Exposed paths:
   - */api/server_info*: return information for the configured server
   - */api/tracks*: return a list of unique tracks stored in db
   - */api/tracks/{track_name}/bestlaps*: return a list of all the best laps for a specific track.  
   - */api/tracks/{track_name}/{car_names}/bestlaps*: return a list of all the best laps for a specific track and cars.  
      Example: ```[..., {"car_name": "ferrari_458_gt2", "track_name": "monza", "driver_name": "FooBar", "best_lap": 426007}, ...]```

## Installation

 ```python setup.py install (virtualenv is recommended)```

### Example crontab job
```*/2 * * * * /opt/assetto_stats_service/python27/bin/acss_cron /path/to/assetto_corsa/dedicated/server/results /opt/assetto_stats_service/acss.db```

### Example supervisord service configuration:
```
 [program:assetto_corsa_stats]
 command=/opt/assetto_stats_service/python27/bin/acssd /opt/assetto_stats_service/etc/acss.conf
 directory=/opt/assetto_stats_service
 numprocs=1
 user=nobody
```
