from tqdm import tqdm


# 将openvpn流进行清洗，只留下相关VPN包以及特征信息，并将这些包根据发送发送方向分为两个列表
def openvpn_cleaner(cap):
    filter_packets = []

    for packet in tqdm(cap, desc="Processing packets", unit="packet"):
        if packet.transport_layer != "UDP" or packet.highest_layer != "DATA" or packet.ip.dst == "255.255.255.255":
            # 丢弃这个包
            continue

        packet_info = {
            'timestamp': packet.sniff_timestamp,  # 获取时间戳
            'length': len(packet),  # 获取包长度（字节数）
            'direction': 0  # 初始化方向，稍后将根据端口号设置
        }

        # 根据目的端口分类
        if packet.udp.dstport == "3001":
            packet_info['direction'] = 1  # 客户端到服务器
        else:
            packet_info['direction'] = -1  # 服务器到客户端
        filter_packets.append(packet_info)

    return filter_packets


# 清洗ike2流
def ike2_cleaner(cap):
    filter_packets = []

    for packet in tqdm(cap, desc="Processing packets", unit="packet"):
        if packet.transport_layer != "UDP" or packet.highest_layer != "DATA" or packet.ip.dst == "255.255.255.255":
            # 丢弃这个包
            continue

        packet_info = {
            'timestamp': packet.sniff_timestamp,  # 获取时间戳
            'length': len(packet),  # 获取包长度（字节数）
            'direction': 0  # 初始化方向，稍后将根据端口号设置
        }
        if packet.udp.dstport == "443":
            packet_info['direction'] = 1  # 客户端到服务器
        else:
            packet_info['direction'] = -1  # 服务器到客户端
        filter_packets.append(packet_info)

    return filter_packets


# 清理sstp流
def sstp_cleaner(cap):
    filter_packets = []

    for packet in tqdm(cap, desc="Processing packets", unit="packet"):
        if packet.highest_layer != "TLS":
            # 丢弃这个包
            continue

        packet_info = {
            'timestamp': packet.sniff_timestamp,  # 获取时间戳
            'length': len(packet),  # 获取包长度（字节数）
            'direction': 0  # 初始化方向，稍后将根据端口号设置
        }
        if packet.tcp.dstport == "443":
            packet_info['direction'] = 1  # 客户端到服务器
        else:
            packet_info['direction'] = -1  # 服务器到客户端
        filter_packets.append(packet_info)

    return filter_packets
