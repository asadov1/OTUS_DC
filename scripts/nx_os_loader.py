# -*- coding: utf-8 -*-

import os
import yaml
from jinja2 import Environment, FileSystemLoader
from netmiko import Netmiko, NetmikoBaseException
from paramiko.ssh_exception import SSHException


def yaml_load(filename):
    with open(filename) as f:
        output = yaml.safe_load(f)
    return output

def generate_config(template, data_dict):
    templ_dir, templ_file = os.path.split(template)

    env = Environment(
        loader=FileSystemLoader(templ_dir), trim_blocks=True, lstrip_blocks=True
    )
    templ = env.get_template(templ_file)
    return templ.render(data_dict)

def send_config_commands(device, config_commands, save_conf=True):
    try:
        with Netmiko(**device) as conn:
            conn.enable()
            output = conn.send_config_set(config_commands)
            if save_conf:
                output += conn.send_command_timing("copy run start")
                output += conn.send_command_timing("y")
            return output
    except (NetmikoBaseException, SSHException) as error:
        print(f"Failed to execute command due to error: {error}")


if __name__ == '__main__':
    template_file = "templates/nexus_conf.txt"
    conf_params = yaml_load("data_files/conf.yaml")
    conn_params = yaml_load("data_files/devices.yaml")

    for device in conn_params:
        device_ip = device["host"]
        device_conf = generate_config(template_file, {"device_params": conf_params['devices'][device_ip]})
        device_conf = device_conf.split('\n')
        print(send_config_commands(device, device_conf))

