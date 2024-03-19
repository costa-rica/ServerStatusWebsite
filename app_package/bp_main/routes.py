from flask import Blueprint
from flask import render_template, send_from_directory, current_app, \
    request, redirect, url_for, flash
import os
import logging
from logging.handlers import RotatingFileHandler
import socket
import subprocess
from app_package.bp_main.utilities import read_syslog_into_list, get_nginx_info, \
    get_terminal_services, read_services_files, merge_and_sort_dfs, \
    df_dict_to_list, check_start_stop
from flask_login import login_required, login_user, logout_user, current_user
import glob
import pandas as pd
import json


bp_main = Blueprint('bp_main', __name__)

formatter = logging.Formatter('%(asctime)s:%(name)s:%(message)s')
formatter_terminal = logging.Formatter('%(asctime)s:%(filename)s:%(name)s:%(message)s')

logger_bp_main = logging.getLogger(__name__)
logger_bp_main.setLevel(logging.DEBUG)

file_handler = RotatingFileHandler(os.path.join(os.environ.get('PROJECT_ROOT'),'logs','main_routes.log'), mode='a', maxBytes=5*1024*1024,backupCount=2)
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
@bp_main.route('/get_aux_images/<aux_dir_name>/<image_dir>/<filename>')
def get_aux_images(aux_dir_name,image_dir, filename):
    logger_bp_main.info(f"- in get_aux_file_from_dir route")
    return send_from_directory(os.path.join(current_app.config.get('DIR_DB_AUXILARY'), aux_dir_name,image_dir), filename)


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
        
    nginx_servers_json_list = get_nginx_info(config_files)

    data = {
        "Proxy Port": [info['proxy_pass'].split(':')[-1] for info in nginx_servers_json_list],
        "Web addresses": [', '.join(info['server_names']) for info in nginx_servers_json_list]
    }

    proxy_port_file = os.path.join(current_app.config.get('DIR_DB_AUXILARY'), "proxy_port.json")

    # create dataframe
    if os.environ.get('FLASK_CONFIG_TYPE') != "local":
        logger_bp_main.info("---> FLASK_CONFIG_TYPE is NOT local <------")
        df = pd.DataFrame(data)
        # sort dataframe by "Proxy Port"
        df["Proxy Port"] = pd.to_numeric(df["Proxy Port"])  # convert "Proxy Port" to numeric so it sorts correctly
        df = df.sort_values("Proxy Port")
        df_dict = df.to_dict('records')

        # create json file using for test
        with open(proxy_port_file, 'w') as pp_file:
            json.dump(data, pp_file)
        
        logger_bp_main.info("---> here is df dict____")
        logger_bp_main.info(df_dict)
        logger_bp_main.info(f"type(df_dict): {type(df_dict)}")
        # logger_bp_main.info(f"df_dict.keys(): {df_dict.keys()}")
        logger_bp_main.info(f"df_dict[0]: {df_dict[0]}")
    else:
        logger_bp_main.info("---> FLASK_CONFIG_TYPE is local <------")
        with open(proxy_port_file, 'r') as pp_file:
            df_dict = json.load(pp_file)

        df_dict = df_dict_to_list(df_dict)
        print("---> here is df dict____")
        print(df_dict)
        print(f"type(df_dict): {type(df_dict)}")
        # print(f"df_dict.keys(): {df_dict.keys()}")
        print(f"df_dict[0]: {df_dict[0]}")
        

    return render_template('main/nginx_servers.html', 
        hostname=hostname,nginx_servers_json_list=nginx_servers_json_list,
        data=data, df_dict=df_dict)



@bp_main.route('/running_services', methods = ['GET', 'POST'])
@login_required
def running_services():
    logger_bp_main.info(f"- in running_services route")
    
    hostname = socket.gethostname()

    if os.environ.get('FLASK_CONFIG_TYPE') == "local":
        # system_file_path = "/Users/nick/Documents/_testData/ServerStatusWebsite/SpeedyProd10/"
        system_file_path = "/Users/nick/Documents/_testData/ServerStatusWebsite/"
        file_name = "system.txt"
        # file = system_file_path + "system_report01/" + file_name
        file = system_file_path + file_name
        with open(file, "r") as f:
            services_from_terminal_data = f.read()

        # service_dir = system_file_path + "etc/systemd/system/"
        service_dir = system_file_path
    else:
        cmd = '/bin/systemctl --type=service'
        services_from_terminal_data = subprocess.check_output(cmd, shell=True, universal_newlines=True)
        service_dir = "/etc/systemd/system/"
        
    terminal_services_df = get_terminal_services(services_from_terminal_data)

    service_files_df = read_services_files(service_dir)

    services_df = merge_and_sort_dfs(terminal_services_df, service_files_df)

    if os.environ.get('FLASK_CONFIG_TYPE') == "local":
        services_df.to_csv(os.path.join(system_file_path,'services_df.csv'))

    # Apply the function to each row in the 'Unit' column and create the 'start_stop' column
    services_df['start_stop'] = services_df['Unit'].apply(check_start_stop)

    df_dict = services_df.to_dict('records')

    if request.method == 'POST':
        formDict = request.form.to_dict()
        print('formDict:::', formDict)
        print('formDict:::', type(formDict))
        service_name= list(formDict.keys())[0]
        print('service_name:::', service_name)
        status = formDict.get(service_name)
        return redirect(url_for('bp_main.manage_service', status = status, service_name = service_name))


    return render_template('main/running_services.html', hostname=hostname,
        df_dict=df_dict, len=len)


@bp_main.route('/manage_service', methods=['GET','POST'])
def manage_service():
    logger_bp_main.info(f"-- accessed: manage_service route")
    status = request.args.get('status', None)
    service_name = request.args.get('service_name', None)

    logger_bp_main.info(f"Managing: {service_name}")
    logger_bp_main.info(f"Current status : {status}")

    if status == 'active':
        status = 'stop'
    else:
        status = 'start'

    if os.environ.get('FLASK_CONFIG_TYPE') != "local":
        # Validate the status argument
        if status not in ['start', 'stop']:
            return jsonify({"error": "Invalid status. Please use 'start' or 'stop'."}), 400

        # Define the systemctl command to run
        # command = f"sudo systemctl {status} WhatSticks10Api_dev"
        command = f"sudo systemctl {status} {service_name}"

        try:
            # Execute the systemctl command
            subprocess.run(command, shell=True, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            # return jsonify({"message": f"The {service_name} service has been {status}ed successfully."}), 200
            flash(f"{service_name} is now {status}","success")
            return redirect(request.referrer)
        except subprocess.CalledProcessError as e:
            # Return an error message if the command execution fails
            logger_bp_main.info(f"Failed to {status} {service_name}. Error: {e}")
            flash(f"{service_name} failed to turn {status}","warning")
            return redirect(url_for('bp_main.running_services'))
    else:
        flash(f"{service_name} is now {status}","success")
        return redirect(request.referrer)




@bp_main.route('/manage_whatsticks10api_dev', methods=['POST'])
def manage_whatsticks10api_dev():

    status = request.args.get('status', None)
    if os.environ.get('FLASK_CONFIG_TYPE') != "local":
        # Validate the status argument
        if status not in ['start', 'stop']:
            return jsonify({"error": "Invalid status. Please use 'start' or 'stop'."}), 400

        # Define the systemctl command to run
        command = f"sudo systemctl {status} WhatSticks10Api_dev"

        try:
            # Execute the systemctl command
            subprocess.run(command, shell=True, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            return jsonify({"message": f"The WhatSticks10Api_dev service has been {status}ed successfully."}), 200
        except subprocess.CalledProcessError as e:
            # Return an error message if the command execution fails
            return jsonify({"error": f"Failed to {status} WhatSticks10Api_dev. Error: {e}"}), 500

