
# Server Status Website

<!-- ![Dashboards and Database Logo](app_package/static/images/DashDataV3_calibri_teal.png) -->
![Ubuntu and DashAndData Logo](https://venturer.dashanddata.com/get_aux_file_from_dir/images/UbuntuAndDashAndData01.png)

## Description
This app is designed to provide information about the Server and the applicaitons running on it. This was created for Ubuntu 20.04 server running Python applications.

Users can login and see the syslog and a table with all the service files and their statuses.


## Installation Instructions
To install the ServerStatusWebsite, you will also need ServerStatusWebsite_modules. Clone the repository and install:
```
git clone [repository-url]
cd ServerStatusWebsite_modules
pip install -e .
```

Then install clone and run ServerStatusWebsite

## Documentation

### Services Link
This is the running_services route that has potential to turn on and off services

#### Step 1: edit /etc/sudoers
From the terminal use `sudo visudo /etc/sudoers`

Below is an excerpt from the /etc/sudoers file. 

The lines that start with "nick" are the ones I added. "nick" in this case is the user and we are editing this file so that a password is not necessary to use the sudo command in this instance.

```
# Allow members of group sudo to execute any command
%sudo   ALL=(ALL:ALL) ALL

# Custom rules for nick to manage specific services without a password
nick ALL=(ALL) NOPASSWD: /bin/systemctl start WhatSticks10Api_dev.service, /bin/systemctl stop WhatSticks10Api_dev.service
nick ALL=(ALL) NOPASSWD: /bin/systemctl start WhatSticks11AppleService_dev.service, /bin/systemctl stop WhatSticks11AppleService_dev.service
nick ALL=(ALL) NOPASSWD: /bin/systemctl start WhatSticks11Scheduler_dev.service, /bin/systemctl stop WhatSticks11Scheduler_dev.service
nick ALL=(ALL) NOPASSWD: /bin/systemctl start WhatSticks11Web_dev.service, /bin/systemctl stop WhatSticks11Web_dev.service

# See sudoers(5) for more information on "#include" directives:

#includedir /etc/sudoers.d
```

#### Step 2: Add/Edit config_ServerStatusWebsite.json
Include START_STOP_LIST with the names of the files in the /etc/sudoers with 
```
	"START_STOP_LIST":["WhatSticks10Api_dev","WhatSticks11AppleService_dev","WhatSticks11Scheduler_dev","WhatSticks11Web_dev"]
```
#### Step 3: Service file 

Below is an example of a the WhatSticks11AppleService.service file. It usually would not have the `WorkingDirectory`, but becuase we need it for the turn-off-turn-on functionality we add it. Then also make sure the full PATH is included in Environment. I have the regular PATH to the venv, but then I added the PATH you can get from the terminal by typing `echo $PATH`.

```
[Unit]
Description= Serve What Sticks 11 Apple Service (queueing) Development.
After=network.target

[Service]
User=nick
WorkingDirectory=/home/nick/applications/WhatSticks11AppleService_dev
Environment=PATH=/home/nick/environments/ws11as_dev/bin:/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin:/usr/games:/usr/local/games:/snap/bin
Environment="FLASK_CONFIG_TYPE=dev"
ExecStart=/home/nick/environments/ws11as_dev/bin/python /home/nick/applications/WhatSticks11AppleService_dev/worker_script.py --serve-in-foreground

[Install]
WantedBy=multi-user.target
```