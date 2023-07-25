from flask import Blueprint
from flask import render_template, send_from_directory, current_app
import os
import logging
from logging.handlers import RotatingFileHandler
import socket
import subprocess
from app_package.bp_main.utilities import read_syslog_into_list, get_nginx_info, \
    services_df, get_services
from flask_login import login_required, login_user, logout_user, current_user
import glob
import pandas as pd


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
    syslog_file = '/var/log/syslog'

    if os.environ.get('FLASK_CONFIG_TYPE') == "local":
        syslog_file = current_app.config.get('LOCAL_TEST_DATA_PATH') + syslog_file

    sys_log_list = read_syslog_into_list(syslog_file)


    return render_template('main/server_syslog.html', hostname=hostname,sys_log_list=sys_log_list)


@bp_main.route('/nginx_servers')
@login_required
def nginx_servers():
    logger_bp_main.info(f"- in nginx_servers route")
    
    hostname = socket.gethostname()

    conf_file_path = '/etc/nginx/conf.d/'

    # if os.environ.get('FLASK_CONFIG_TYPE') == "prod":
    config_files = glob.glob(conf_file_path + '*.conf')  # get all .conf files in /etc/nginx/conf.d/
    # nginx_servers_json_list = get_nginx_info(config_files)
    if os.environ.get('FLASK_CONFIG_TYPE') == "local":
        config_files = glob.glob(current_app.config.get('LOCAL_TEST_DATA_PATH') + conf_file_path + '*.conf')  # get all .conf files in /etc/nginx/conf.d/
        
        # nginx_servers_json_list = [{"message":f"Not production machine: {hostname}"}]

    nginx_servers_json_list = get_nginx_info(config_files)

    data = {
        "Proxy Port": [info['proxy_pass'].split(':')[-1] for info in nginx_servers_json_list],
        "Web addresses": [', '.join(info['server_names']) for info in nginx_servers_json_list]
    }

    # create dataframe
    df = pd.DataFrame(data)
    # sort dataframe by "Proxy Port"
    df["Proxy Port"] = pd.to_numeric(df["Proxy Port"])  # convert "Proxy Port" to numeric so it sorts correctly
    df = df.sort_values("Proxy Port")
    df_dict = df.to_dict('records')
    print(df_dict)


    return render_template('main/nginx_servers.html', 
        hostname=hostname,nginx_servers_json_list=nginx_servers_json_list,
        data=data, df_dict=df_dict)



@bp_main.route('/running_services')
@login_required
def running_services():
    logger_bp_main.info(f"- in running_services_list route")
    
    hostname = socket.gethostname()

    directory = "/etc/systemd/system"
    if os.environ.get('FLASK_CONFIG_TYPE') == "local":
        directory = current_app.config.get('LOCAL_TEST_DATA_PATH') + directory 
        
    # df = services_df(directory)
    # df_dict = df.to_dict('records')
    df = get_services()
    df_dict = df.to_dict('records')

    return render_template('main/running_services.html', hostname=hostname,
        df_dict=df_dict)

