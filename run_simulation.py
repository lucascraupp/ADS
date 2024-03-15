import csv
import os
import subprocess

ALG = ["cubic", "reno"]
IMUNES_PATH = "./mini_projeto.imn"
EXPERIMENT_ID = "19669"
BER = ["100000", "1000000"]
E2E_DELAY = ["10000", "100000"]
REPETITION = 8
IP = {"pc1": "10.0.0.20", "pc2": "10.0.1.20", "pc3": "10.0.3.20", "pc4": "10.0.4.20"}
EXECUTION_TIME = 1000
UDP_BANDWIDTH = "10M"


def run_imunes():
    if not os.path.exists(IMUNES_PATH) and not IMUNES_PATH.endswith(".imn"):
        raise FileNotFoundError("arquivo IMUNES não encontrado!")
    else:
        print("Rodando a simulação...")

        cmd = f"sudo imunes -b -e {EXPERIMENT_ID} {IMUNES_PATH}"

        subprocess.run(cmd, shell=True)


def run_experiment():
    cmd_iperf_server_tcp = f"sudo himage pc2@{EXPERIMENT_ID} iperf -s &"

    cmd_iperf_server_udp = f"sudo himage pc4@{EXPERIMENT_ID} iperf -s -u &"
    cmd_iperf_client_udp = f"sudo himage pc3@{EXPERIMENT_ID} iperf -c {IP['pc4']} -u -t {EXECUTION_TIME} -b {UDP_BANDWIDTH} &"

    subprocess.run(cmd_iperf_server_udp, shell=True)
    subprocess.run(cmd_iperf_server_tcp, shell=True)
    subprocess.run(cmd_iperf_client_udp, shell=True)

    for rep in range(REPETITION):
        for proto in ALG:
            for ber in BER:
                for e2e in E2E_DELAY:
                    cmd_iperf_echo = f"echo -n {rep},{proto},{ber},{e2e},{UDP_BANDWIDTH}, >> dados.csv"
                    subprocess.run(cmd_iperf_echo, shell=True)

                    cmd_iperf_vlink_and_delay = f"sudo vlink -BER {ber} -d {e2e} router1:router2@ {EXPERIMENT_ID} >> dados.csv"
                    subprocess.run(cmd_iperf_vlink_and_delay, shell=True)

                    cmd_iperf_client_tcp = f"sudo himage pc1@{EXPERIMENT_ID} iperf -c {IP['pc2']} -y C -Z {proto} >> dados.csv"
                    subprocess.run(cmd_iperf_client_tcp, shell=True)

    subprocess.Popen(["cleanupAll"]).wait()


run_imunes()
run_experiment()
