import os
import re
import glob
import subprocess

def read_syslog_into_list(syslog_file):
    sys_log_list = []
    try:
        with open(syslog_file, 'r') as f:
            sys_log_list = f.readlines()
    except FileNotFoundError:
        print(f"{syslog_file} not found.")
    except Exception as e:
        print(f"An error occurred: {e}")
    
    return sys_log_list


def get_nginx_info():
    nginx_info = []
    
    config_files = glob.glob('/etc/nginx/conf.d/*.conf')  # get all .conf files in /etc/nginx/conf.d/

    for file in config_files:
        with open(file, 'r') as f:
            lines = f.readlines()
            
        # temporary dictionary to store info of current server block
        server_info = {}
        for line in lines:
            if 'server_name' in line:
                server_names = line.split()[1:]  # remove 'server_name'
                server_names[-1] = server_names[-1][:-1]  # remove semicolon at the end
                server_info['server_names'] = server_names
                
            elif 'proxy_pass' in line:
                proxy_pass = line.split()[1][:-1]  # remove 'proxy_pass' and semicolon at the end
                server_info['proxy_pass'] = proxy_pass
                
            elif 'listen' in line and ('ssl' not in line):
                port = line.split()[1].split(';')[0]  # get port number
                server_info['port'] = port

        if server_info:  # if server_info is not empty
            nginx_info.append(server_info)

    return nginx_info