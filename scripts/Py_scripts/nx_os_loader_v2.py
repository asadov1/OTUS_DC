# -*- coding: utf-8 -*-

import os
import yaml
from jinja2 import Environment, FileSystemLoader
from netmiko import Netmiko, NetmikoBaseException
from paramiko.ssh_exception import SSHException
from isis_net_converting import isis_net
from concurrent.futures import ThreadPoolExecutor


def yaml_load(filename):
    with open(filename) as f:
        output = yaml.safe_load(f)
    return output

def generate_config(template, data_dict):
    templ_dir, templ_file = os.path.split(template)

    env = Environment(
        loader=FileSystemLoader(templ_dir), trim_blocks=True, lstrip_blocks=True
    )
    env.filters["isis_net"] = isis_net
    templ = env.get_template(templ_file)
    return templ.render(data_dict)

def send_config_commands(device, config_commands, save_conf=False):
    try:
        with Netmiko(**device) as conn:
            conn.enable()
            output = conn.send_config_set(config_commands)
            if save_conf:
                output += conn.send_command_timing("copy run start")
                # output += conn.send_command_timing("y")
            return output
    except (NetmikoBaseException, SSHException) as error:
        print(f"Failed to execute command due to error: {error}")


def send_config_commands_to_devices(devices, config_commands, save_conf=False, limit=10):
    with ThreadPoolExecutor(max_workers=limit) as executor:
        futures = []
        for device, command in zip(devices, config_commands):
            future = executor.submit(send_config_commands, device, command, save_conf)
            futures.append(future)

        results = []
        for future in futures:
            try:
                result = future.result()
                results.append(result)
            except Exception as e:
                print(f"Task resulted in an exception: {e}")
    return results


if __name__ == '__main__':
    template_file = "templates/eos/underlay/eos_conf.j2"
    conf_params = yaml_load("data_files/conf_underlay.yml")
    conn_params = yaml_load("data_files/devices_eos.yml")

    devices_configs = []
    for device in conn_params:
        device_ip = device["host"]
        device_conf = generate_config(template_file,
                                      {"device_params": conf_params['devices'][device_ip]}).split('\n')
        devices_configs.append(device_conf)

    print(send_config_commands_to_devices(conn_params, devices_configs))