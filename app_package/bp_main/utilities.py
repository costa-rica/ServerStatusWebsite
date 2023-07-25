import os
import re
# import glob
import subprocess
# import os
import pandas as pd
# import subprocess
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
    sys_log_list.reverse()
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



def services_df(directory):
    # The directory where service files are stored in Ubuntu
    # directory = "/etc/systemd/system"

    # Lists to store the results
    filenames = []
    users = []
    execstarts = []
    statuses = []

    # Traverse the directory
    for filename in os.listdir(directory):
        if filename.endswith(".service"):
            # Full path to the service file
            filepath = os.path.join(directory, filename)
            
            user = ""
            execstart = ""

            # Read the service file
            with open(filepath, "r") as file:
                for line in file.readlines():
                    line = line.strip()

                    # Find the User line
                    if line.startswith("User="):
                        user = line.split("=")[1].strip()

                    # Find the ExecStart line
                    if line.startswith("ExecStart="):
                        execstart = line.split("=")[1].strip()

            # Append the results
            filenames.append(filename)
            users.append(user)
            execstarts.append(execstart)

            # Get the status of the service
            try:
                output = subprocess.check_output(["sudo", "systemctl", "is-active", filename], universal_newlines=True)
                statuses.append(output.strip())
            except subprocess.CalledProcessError as e:
                statuses.append(e)
            except:
                statuses.append("unknown")

    # Create a DataFrame
    df = pd.DataFrame({
        "Filename": filenames,
        "User": users,
        "ExecStart": execstarts,
        "Status": statuses
    })

    # # Print the DataFrame
    # print(df)
    return df


def get_services():
    # try:
    # Execute the command and get the output
    cmd = '/bin/systemctl --type=service'
    result = subprocess.check_output(cmd, shell=True, universal_newlines=True)

    # Split the output into lines
    lines = result.strip().split('\n')

    # Split each line into columns and remove unnecessary whitespace
    data = [line.split() for line in lines]

    # Convert the list of lists into a DataFrame
    df = pd.DataFrame(data)
    print(df)

    return df

    # except Exception as e:
    #     print(f"Error occurred: {e}")
    #     return None

