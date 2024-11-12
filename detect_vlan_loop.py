import psutil
from scapy.all import sniff, Dot1Q, STP
from collections import defaultdict
import time

# Ağ arayüzünü otomatik olarak algılayan fonksiyon
def get_active_interface():
    for interface, addrs in psutil.net_if_addrs().items():
        # Her arayüz için adresleri kontrol et
        for addr in addrs:
            if addr.family == psutil.AF_LINK:  # MAC adresi varsa
                # Bağlantı durumu UP olan ilk arayüzü döndür
                stats = psutil.net_if_stats()[interface]
                if stats.isup:  # Eğer arayüz aktifse
                    return interface
    return None

# MAC adresleri ve VLAN ID'lere göre en son görülme zamanlarını tutacak sözlük
mac_vlan_last_seen = defaultdict(lambda: 0)

# Aynı MAC adresinden aynı VLAN üzerinde gelen paketler arasındaki süre eşiği
TIME_THRESHOLD = 1  # saniye cinsinden (gerekirse VLAN başına farklı tanımlanabilir)

# Her VLAN için root bridge MAC adresini takip eden sözlük
root_bridge_mac = {}

def detect_vlan_loop_and_root_bridge(packet):
    # STP çerçevesi varsa root bridge adresini kontrol et
    if packet.haslayer(STP):
        vlan_id = packet[Dot1Q].vlan if packet.haslayer(Dot1Q) else "default"  # Dot1Q yoksa "default" VLAN kabul edilir
        root_mac = packet[STP].rootmac  # STP katmanından root MAC adresini al

        # İlk root bridge adresini ayarla ya da değişiklik kontrolü yap
        if vlan_id not in root_bridge_mac:
            root_bridge_mac[vlan_id] = root_mac
            print(f"Initial Root Bridge MAC for VLAN {vlan_id}: {root_mac}")
        elif root_bridge_mac[vlan_id] != root_mac:
            print(f"Root Bridge MAC changed for VLAN {vlan_id}: {root_bridge_mac[vlan_id]} -> {root_mac}")
            root_bridge_mac[vlan_id] = root_mac  # Yeni root bridge MAC adresini güncelle

    # Loop kontrolü
    if packet.haslayer("Ether"):
        src_mac = packet.src
        vlan_id = packet[Dot1Q].vlan if packet.haslayer(Dot1Q) else "default"  # Dot1Q yoksa "default" VLAN kabul edilir
        current_time = time.time()
        
        # Her VLAN ID ve MAC adres çifti için son görülme zamanına bak
        mac_vlan_key = (src_mac, vlan_id)
        
        if mac_vlan_key in mac_vlan_last_seen:
            last_seen_time = mac_vlan_last_seen[mac_vlan_key]
            time_diff = current_time - last_seen_time
            
            # Eğer paketler arasında belirli bir süreden az fark varsa, bir loop oluşmuş olabilir
            if time_diff < TIME_THRESHOLD:
                print(f"Loop detected! MAC Address: {src_mac}, VLAN: {vlan_id}, Interval: {time_diff:.2f} seconds")
        
        # En son görülme zamanını güncelle
        mac_vlan_last_seen[mac_vlan_key] = current_time

# Ağ arayüzünü otomatik olarak algıla
interface = get_active_interface()

# Algılanan arayüzü kontrol et
if interface:
    print(f"Listening on automatically detected interface: {interface} for potential VLAN loops and root bridge changes...")
    sniff(iface=interface, prn=detect_vlan_loop_and_root_bridge, store=0)
else:
    print("No active network interface found. Please connect to the network and try again.")
