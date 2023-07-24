from flask import Blueprint
from flask import render_template, send_from_directory, current_app
import os
import logging
from logging.handlers import RotatingFileHandler
import socket
import subprocess
from app_package.bp_main.utilities import read_syslog_into_list, get_nginx_info
from flask_login import login_required, login_user, logout_user, current_user


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
    hostname = socket.gethostname()
    return render_template('main/home.html', hostname=hostname)

# Custom static data - DIR_DB_AUXILARY (/_databases/dashAndData07/auxilary/<aux_dir_name>/<filename>)
@bp_main.route('/get_aux_file_from_dir/<aux_dir_name>/<filename>')
def get_aux_file_from_dir(aux_dir_name, filename):
    logger_bp_main.info(f"- in get_aux_file_from_dir route")
    return send_from_directory(os.path.join(current_app.config.get('DIR_DB_AUXILARY'), aux_dir_name), filename)

# Custom static data - DIR_DB_AUXILARY (/_databases/dashAndData07/auxilary/<aux_dir_name>/<filename>)
@bp_main.route('/server_syslog')
@login_required
def server_syslog():
    logger_bp_main.info(f"- in server_syslog route")
    
    hostname = socket.gethostname()
    if os.environ.get('FLASK_CONFIG_TYPE') == "prod":
        syslog_file = '/var/log/syslog'
    else:
        syslog_file = '/Users/nick/Documents/_testData/ServerStatusWebsite/syslog'
    sys_log_list = read_syslog_into_list(syslog_file)
    # try:
    #     with open(syslog_file, 'r') as f:
    #         sys_log_list = f.readlines()
    # except FileNotFoundError:
    #     print(f"{syslog_file} not found.")
    # except Exception as e:
    #     print(f"An error occurred: {e}")
    # return sys_log_list

    return render_template('main/server_syslog.html', hostname=hostname,sys_log_list=sys_log_list)


@bp_main.route('/nginx_servers')
@login_required
def nginx_servers():
    logger_bp_main.info(f"- in nginx_servers route")
    
    hostname = socket.gethostname()
    # if os.environ.get('FLASK_CONFIG_TYPE') == "prod":
    #     syslog_file = '/var/log/syslog'
    # else:
    #     syslog_file = '/Users/nick/Documents/_testData/ServerStatusWebsite/syslog'
    if os.environ.get('FLASK_CONFIG_TYPE') == "prod":
        nginx_servers_json_list = get_nginx_info()
    else:
        nginx_servers_json_list = [{"message":f"Not production machine: {hostname}"}]


    return render_template('main/nginx_servers.html', 
        hostname=hostname,nginx_servers_json_list=nginx_servers_json_list)



@bp_main.route('/running_services')
@login_required
def running_services():
    logger_bp_main.info(f"- in running_services_list route")
    
    hostname = socket.gethostname()
    if os.environ.get('FLASK_CONFIG_TYPE') == "prod":
        syslog_file = '/var/log/syslog'
    else:
        syslog_file = '/Users/nick/Documents/_testData/ServerStatusWebsite/syslog'

 


    return render_template('main/running_services.html', hostname=hostname,running_services_list=running_services_list)


