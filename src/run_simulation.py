import os
import subprocess

ALG = ["cubic", "reno"]
IMUNES_PATH = "data/mini_projeto.imn"
CSV_PATH = "data/dados.csv"
EXPERIMENT_ID = "19669"
BER = ["100000", "1000000"]
E2E_DELAY = ["10000", "100000"]
REPETITION = 8
IP = {"pc1": "10.0.0.20", "pc2": "10.0.1.20", "pc3": "10.0.3.20", "pc4": "10.0.4.20"}
EXECUTION_TIME = 1000
UDP_BANDWIDTH = "10M"
COLUMNS_NAME = [
    "Repetição",
    "Protocolo",
    "BER",
    "Delay",
    "Largura de Banda UDP",
    "Timestamp",
    "IP PC1",
    "Porta PC1",
    "IP PC2",
    "Porta PC2",
    "ID",
    "Intervalo",
    "Taxa de Transferência",
    "Largura de Banda TCP",
]


def run_imunes():
    if not os.path.exists(IMUNES_PATH) and not IMUNES_PATH.endswith(".imn"):
        raise FileNotFoundError("arquivo IMUNES não encontrado!")
    else:
        print("Rodando a simulação...")

        if os.path.exists(CSV_PATH):
            os.remove(CSV_PATH)

        cmd = f"sudo imunes -b -e {EXPERIMENT_ID} {IMUNES_PATH}"

        subprocess.run(cmd, shell=True)


def run_experiment():
    run_imunes()

    cmd_iperf_server_tcp = f"sudo himage pc2@{EXPERIMENT_ID} iperf -s &"

    cmd_iperf_server_udp = f"sudo himage pc4@{EXPERIMENT_ID} iperf -s -u &"
    cmd_iperf_client_udp = f"sudo himage pc3@{EXPERIMENT_ID} iperf -c {IP['pc4']} -u -t {EXECUTION_TIME} -b {UDP_BANDWIDTH} &"

    subprocess.run(cmd_iperf_server_udp, shell=True)
    subprocess.run(cmd_iperf_server_tcp, shell=True)
    subprocess.run(cmd_iperf_client_udp, shell=True)

    for col in COLUMNS_NAME[:-1]:
        subprocess.run(f"echo -n {col}, >> {CSV_PATH}", shell=True)

    subprocess.run(f"echo {COLUMNS_NAME[-1]} >> {CSV_PATH}", shell=True)

    for rep in range(REPETITION):
        for proto in ALG:
            for ber in BER:
                for e2e in E2E_DELAY:
                    cmd_iperf_echo = f"echo -n {rep},{proto},{ber},{e2e},{UDP_BANDWIDTH}, >> {CSV_PATH}"
                    subprocess.run(cmd_iperf_echo, shell=True)

                    cmd_iperf_vlink_and_delay = f"sudo vlink -BER {ber} -d {e2e} router1:router2@ {EXPERIMENT_ID} >> {CSV_PATH}"
                    subprocess.run(cmd_iperf_vlink_and_delay, shell=True)

                    cmd_iperf_client_tcp = f"sudo himage pc1@{EXPERIMENT_ID} iperf -c {IP['pc2']} -y C -Z {proto} >> {CSV_PATH}"
                    subprocess.run(cmd_iperf_client_tcp, shell=True)

    subprocess.Popen(["sudo", "cleanupAll"]).wait()


run_experiment()
