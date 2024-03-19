import os
import re
# import glob
import subprocess
# import os
import pandas as pd
from flask import current_app
if os.environ.get('FLASK_CONFIG_TYPE') != "local":
    from systemd import journal

def read_syslog_into_list(syslog_file):
    sys_log_list = []
    try:
        with open(syslog_file, 'r') as f:
            sys_log_list = f.readlines()
    except FileNotFoundError:
        print(f"{syslog_file} not found.")
    except Exception as e:
        print(f"An error occurred: {e}")
    sys_log_list
    return sys_log_list


def get_nginx_info(config_files):
    nginx_info = []
    
    

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

def write_nginx_info_to_excel(nginx_info):
    # prepare data for dataframe
    data = {
        "Proxy Port": [info['proxy_pass'].split(':')[-1] for info in nginx_info],
        "Web addresses": [', '.join(info['server_names']) for info in nginx_info]
    }

    # create dataframe
    df = pd.DataFrame(data)

    # write dataframe to Excel file
    df.to_excel('nginx_info.xlsx', index=False)




def get_terminal_services(data):
    # cmd = '/bin/systemctl --type=service'
    # result = subprocess.check_output(cmd, shell=True, universal_newlines=True)
    lines = data.strip().split('\n')
    data = []
    for line in lines:
        # print("----")
        # print(line)
        # Stop processing if we encounter the "LOAD =" row
        if line.startswith("LOAD   ="):
            break
        elif line.startswith("UNIT   "):
            continue

        # Skip the line if it starts with '●'
        if line.startswith('●'):
            line = line[1:]

        # Split the line into words
        words = line.split()

        try:
            # The first three columns are always single words
            unit, load, sub = words[:3]

            # The remaining words belong to the description, which can contain spaces
            description = ' '.join(words[3:])

            data.append([unit, load, sub, description])
        except ValueError as e:
            print(f"Error occurred: {e}")
            # print(line)

    # Convert the list of lists into a DataFrame
    terminal_services_df = pd.DataFrame(data, columns=['Unit', 'Load', 'Sub', 'Description'])
    # terminal_services_df.to_excel("_terminal_services_df.xlsx")
    return terminal_services_df


def read_services_files(service_dir):
    # service_dir = "/etc/systemd/system/"
    data = {'FileName': [], 'User': [], 'WorkingDirectory': [], 'ExecStart': []}
    # print("------")
    # print(service_dir)
    for filename in os.listdir(service_dir):
        if filename.endswith(".service"):
            with open(os.path.join(service_dir, filename), 'r') as file:
                content = file.readlines()

            data['FileName'].append(filename)

            user_line = [line for line in content if line.startswith('User')]
            user = user_line[0].split('=')[1].strip() if user_line else None
            data['User'].append(user)

            wd_line = [line for line in content if line.startswith('WorkingDirectory')]
            wd = wd_line[0].split('=')[1].strip().split('/')[-1] if wd_line else None
            data['WorkingDirectory'].append(wd)

            execstart_line = [line for line in content if line.startswith('ExecStart')]
            execstart = re.findall(r':(\d+)', execstart_line[0]) if execstart_line else None
            execstart = execstart[0] if execstart else None
            data['ExecStart'].append(execstart)

    service_files_df = pd.DataFrame(data)
    # service_files_df.to_excel("_service_files_df.xlsx")
    return service_files_df



def merge_and_sort_dfs(terminal_services_df, service_files_df):

    # Merge the dataframes on 'Unit'/'Service' columns
    services_df = pd.merge(terminal_services_df, service_files_df, how='outer', left_on='Unit', right_on='FileName')

    # Create helper columns for sorting
    services_df['User_exists'] = services_df['User'].notna()
    services_df['Sub_active'] = services_df['Sub'] == 'active'

    # Sort by 'User_exists' (True first), then by 'Sub_active' (True first)
    services_df.sort_values(['User_exists', 'Sub_active'], ascending=[False, False], inplace=True)

    # Reset the index to reflect sorted order, without dropping it
    services_df.reset_index(inplace=True)

    # Rename the new column to 'Index'
    services_df.rename(columns={'index': 'Index'}, inplace=True)
    services_df.drop(['Index'], axis=1, inplace=True)

    # Reset the index to reflect sorted order, without dropping it
    services_df.reset_index(inplace=True)
    services_df.rename(columns={'index': 'Index'}, inplace=True)
    # Drop helper columns
    services_df.drop(['User_exists', 'Sub_active'], axis=1, inplace=True)
    # services_df.to_excel("_services_df.xlsx")
    return services_df

    # # Merge the dataframes on 'Unit'/'Service' columns
    # services_df = pd.merge(terminal_services_df, service_files_df, how='outer', left_on='Unit', right_on='FileName')

    # # First, sort by 'User', putting non-empty values on top
    # services_df['User'] = services_df['User'].replace({None: pd.NA})
    # services_df = services_df.sort_values('User', na_position='last')
    # services_df.to_excel("_services_df.xlsx")
    # # Then, sort by 'Sub', putting 'active' on top
    # services_df['Sub'] = services_df['Sub'].replace({'active': 1, None: 2}).fillna(3)
    # services_df = services_df.sort_values('Sub')

    # return services_df

def df_dict_to_list(data):


    # 2. Parse the content of the file using the json module to get the dictionary.
    proxy_ports = data["Proxy Port"]
    web_addresses = data["Web addresses"]

    # 3. Zip the "Proxy Port" and "Web addresses" lists together.
    paired_data = list(zip(proxy_ports, web_addresses))

    # 4. Convert the zipped pairs into a list of dictionaries.
    result = [{"Proxy Port": int(port), "Web addresses": address} for port, address in paired_data]

    # 5. Sort the list of dictionaries based on the "Proxy Port".
    result = sorted(result, key=lambda x: x["Proxy Port"])

    # Print the result
    return(result)

# Function to check if the unit matches any in the start_stop_list
def check_start_stop(unit):
    start_stop_list = current_app.config.get('START_STOP_LIST')
    
    try:
        # unit_cleaned = unit.replace('.service', '')
        # Check if the cleaned unit is in the start_stop_list
        if unit in start_stop_list:
            return unit_cleaned
        else:
            return ''
    except:
        return ''



