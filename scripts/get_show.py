import yaml
from pprint import pprint
from netmiko import Netmiko, NetmikoBaseException
from paramiko.ssh_exception import SSHException


def yaml_load(filename):
    with open(filename) as f:
        output = yaml.safe_load(f)
    return output

def send_show_command(device, commands):
    try:
        with Netmiko(**device) as ssh:
            ssh.enable()
            output = ""
            for command in commands:
                promt = ssh.find_prompt()
                output += ssh.send_command(command)
            output += "="*40
        return f"{promt}{output}"
    except (NetmikoBaseException, SSHException) as error:
        print(error)


if __name__ == "__main__":
    commands = ["sh run ospf", "sh run int"]
    conn_params = yaml_load("data_files/devices.yaml")
    for dev in conn_params:
        print(send_show_command(dev, commands))