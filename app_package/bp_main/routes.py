from flask import Blueprint
from flask import render_template, send_from_directory
import os
import logging
from logging.handlers import RotatingFileHandler
import socket
import subprocess


bp_main = Blueprint('bp_main', __name__)

formatter = logging.Formatter('%(asctime)s:%(name)s:%(message)s')
formatter_terminal = logging.Formatter('%(asctime)s:%(filename)s:%(name)s:%(message)s')

logger_bp_main = logging.getLogger(__name__)
logger_bp_main.setLevel(logging.DEBUG)

file_handler = RotatingFileHandler(os.path.join(os.environ.get('WEB_ROOT'),'logs','main_routes.log'), mode='a', maxBytes=5*1024*1024,backupCount=2)
file_handler.setFormatter(formatter)

stream_handler = logging.StreamHandler()
stream_handler.setFormatter(formatter_terminal)

logger_bp_main.addHandler(file_handler)
logger_bp_main.addHandler(stream_handler)


@bp_main.route("/", methods=["GET","POST"])
def home():
    logger_bp_main.info(f"-- in home page route --")

    return render_template('main/home.html')

# Custom static data - DIR_DB_AUXILARY (/_databases/dashAndData07/auxilary/<aux_dir_name>/<filename>)
@bp_main.route('/get_aux_file_from_dir/<aux_dir_name>/<filename>')
def get_aux_file_from_dir(aux_dir_name, filename):
    logger_bp_main.info(f"- in get_aux_file_from_dir route")
    return send_from_directory(os.path.join(current_app.config.get('DIR_DB_AUXILARY'), aux_dir_name), filename)

# Custom static data - DIR_DB_AUXILARY (/_databases/dashAndData07/auxilary/<aux_dir_name>/<filename>)
@bp_main.route('/server_syslog')
def server_syslog():
    logger_bp_main.info(f"- in server_syslog route")
    
    hostname = socket.gethostname()
    if os.environ.get('FLASK_CONFIG_TYPE') == "prod":
        syslog_file = '/var/log/syslog'
    else:
        syslog_file = '/Users/nick/Documents/_testData/ServerStatusWebsite/syslog'
    sys_log_list = []
    try:
        with open(syslog_file, 'r') as f:
            sys_log_list = f.readlines()
    except FileNotFoundError:
        print(f"{syslog_file} not found.")
    except Exception as e:
        print(f"An error occurred: {e}")
    # return sys_log_list

    return render_template('main/server_syslog.html', hostname=hostname,sys_log_list=sys_log_list)


@bp_main.route('/nginx_servers')
def nginx_servers():
    logger_bp_main.info(f"- in nginx_servers route")
    
    hostname = socket.gethostname()
    # if os.environ.get('FLASK_CONFIG_TYPE') == "prod":
    #     syslog_file = '/var/log/syslog'
    # else:
    #     syslog_file = '/Users/nick/Documents/_testData/ServerStatusWebsite/syslog'
    if os.environ.get('FLASK_CONFIG_TYPE') == "prod":
        # Run the command and capture the output
        command = ["grep", "-rnE", "/etc/nginx/", "-e", "server_name", "-e", "proxy_pass"]
        result = subprocess.run(command, capture_output=True, text=True)

        # Parse the output into a list of dictionaries
        lines = result.stdout.strip().split("\n")
        parsed = []
        for line in lines:
            file, line, text = line.split(":", 2)
            parsed.append({
                "file": file,
                "line": int(line),
                "text": text.strip(),
            })

        # Serialize the parsed output to JSON
        nginx_servers_json = json.dumps(parsed, indent=4)
    else:
        nginx_servers_json = {"message":f"Not production machine: {hostname}"}


    return render_template('main/nginx_servers.html', hostname=hostname,nginx_servers_json=nginx_servers_json)



@bp_main.route('/running_services')
def running_services():
    logger_bp_main.info(f"- in running_services_list route")
    
    hostname = socket.gethostname()
    if os.environ.get('FLASK_CONFIG_TYPE') == "prod":
        syslog_file = '/var/log/syslog'
    else:
        syslog_file = '/Users/nick/Documents/_testData/ServerStatusWebsite/syslog'

 


    return render_template('main/running_services.html', hostname=hostname,running_services_list=running_services_list)


