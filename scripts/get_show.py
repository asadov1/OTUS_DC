# -*- coding: utf-8 -*-

from netmiko import Netmiko, NetmikoBaseException
from paramiko.ssh_exception import SSHException
from old_scripts.nx_os_loader_v1 import yaml_load

def send_show_command(device, commands):
    try:
        with Netmiko(**device) as ssh:
            ssh.enable()
            output = ""
            for command in commands:
                prompt = ssh.find_prompt()
                output += ssh.send_command(command)
            output += "="*40
            filename = "files/get_conf.txt"
        with open(filename, "a") as f:
            f.write(f"{prompt}{output}")
        return f"{prompt}{output}"
    except (NetmikoBaseException, SSHException) as error:
        print(error)

if __name__ == "__main__":
    commands = ["sh run"]
    conn_params = yaml_load("data_files/devices_eos.yml")
    for dev in conn_params:
        print(send_show_command(dev, commands))