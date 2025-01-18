import csv
import os
import pyshark
from pcapng_processor import *


# 将pcapng文件中需要的数据写入csv文件
def pcapng_to_csv(protocal):
    directory = "../data/" + str(protocal)
    for root, dirs, files in os.walk(directory):
        for file in files:
            filename = "../data/" + str(protocal) + "/" + str(file)
            csv_filepath = "../csv_data/" + str(protocal) + "/" + file.rsplit('.', 1)[0] + ".csv"

            print(f"Generating CSV_file: {csv_filepath}")
            cap = pyshark.FileCapture(filename, tshark_path="D:\\wireshark\\tshark.exe")
            if protocal == "ike2":
                filter_packets = ike2_cleaner(cap)
            elif protocal == "openvpn":
                filter_packets = openvpn_cleaner(cap)
            else:
                filter_packets = sstp_cleaner(cap)
            cap.close()

            save_to_csv(filter_packets, csv_filepath)


# 写入csv文件
def save_to_csv(all_packets, filename):
    fieldnames = ['timestamp', 'length', 'direction']
    with open(filename, mode='w', newline='') as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        for packet in all_packets:
            writer.writerow(packet)


# 运行本文件将pcapng文件转化为csv文件
if __name__ == "__main__":
    # "ike2", "openvpn", "sstp"
    protocals = ["sstp"]
    for ptc in protocals:
        pcapng_to_csv(ptc)

    # # test
    # cap = pyshark.FileCapture("../test_sstp.pcapng", tshark_path="D:\\wireshark\\tshark.exe")
    # filter_packets = sstp_cleaner(cap)
    # cap.close()
    # save_to_csv(filter_packets, "../csv_data/test.csv")
