import socket
import struct
import time
import os
import sys
import argparse

class ICMPPacket:
    def __init__(self, is_ipv6=False):
        self.type = 128 if is_ipv6 else 8  # Echo request: 8 for IPv4, 128 for IPv6
        self.code = 0
        self.checksum = 0
        self.id = os.getpid() & 0xFFFF
        self.sequence = 0
        self.is_ipv6 = is_ipv6

    def create_packet(self, sequence):
        self.sequence = sequence
        header = struct.pack('!BBHHH', self.type, self.code, 0, self.id, self.sequence)
        data = b'abcdefghijklmnopqrstuvwabcdefghi'  # 32 bytes of data
        packet = header + data
        self.checksum = self._calculate_checksum(packet)
        header = struct.pack('!BBHHH', self.type, self.code, self.checksum, self.id, self.sequence)
        return header + data

    def _calculate_checksum(self, data):
        checksum = 0
        if len(data) % 2:
            data += b'\0'
        for i in range(0, len(data), 2):
            word = (data[i] << 8) + data[i + 1]
            checksum += word
        while checksum >> 16:
            checksum = (checksum & 0xffff) + (checksum >> 16)
        return ~checksum & 0xffff

class PingUtility:
    def __init__(self, target, count=4, ttl=64, timeout=2):
        self.target = target
        self.count = count
        self.ttl = ttl
        self.timeout = timeout
        self.sent = 0
        self.received = 0
        self.rtt_list = []
        self.is_ipv6 = self._determine_ip_version()
        self.ipv6_supported = hasattr(socket, 'IPPROTO_ICMPV6')

    def _determine_ip_version(self):
        try:
            socket.inet_pton(socket.AF_INET6, self.target)
            return True
        except socket.error:
            try:
                socket.inet_pton(socket.AF_INET, self.target)
                return False
            except socket.error:
                print(f"DEBUG: Target {self.target} is not a valid IP, attempting hostname resolution")
                try:
                    addrinfo = socket.getaddrinfo(self.target, None, socket.AF_INET6)
                    return True if addrinfo and addrinfo[0][0] == socket.AF_INET6 else False
                except socket.gaierror:
                    return False

    def ping(self):
        try:
            target_ip = self.target
            if not self._is_valid_ip(self.target):

                target_ip = socket.getaddrinfo(self.target, None, socket.AF_INET6 if self.is_ipv6 else socket.AF_INET)[0][4][0]


            family = socket.AF_INET6 if self.is_ipv6 else socket.AF_INET
            proto = socket.IPPROTO_ICMPV6 if self.is_ipv6 else socket.IPPROTO_ICMP
            ttl_option = socket.IPV6_HOPLIMIT if self.is_ipv6 else socket.IP_TTL

            print(f"PING {self.target} ({target_ip}) 32 bytes of data:")


            if self.is_ipv6 and not self.ipv6_supported:
                raise ValueError("IPv6 ICMP (ICMPv6) is not supported on this system")

            # Create raw socket
            sock = socket.socket(family, socket.SOCK_RAW, proto)

            for seq in range(self.count):
                icmp = ICMPPacket(is_ipv6=self.is_ipv6)
                packet = icmp.create_packet(seq)

                start_time = time.time()
                bytes_sent = sock.sendto(packet, (target_ip, 0))
                self.sent += 1


                while True:
                    try:
                        reply, addr = sock.recvfrom(1024)
                        end_time = time.time()
                        rtt = (end_time - start_time) * 1000
                        if self._process_reply(reply, seq, icmp.id):
                            self.received += 1
                            self.rtt_list.append(rtt)
                            print(f"64 bytes from {addr[0]}: icmp_seq={seq} ttl={self.ttl} time={rtt:.2f} ms")
                            break
                    except socket.timeout:
                        print(f"Request timeout for icmp_seq {seq}")
                        break

                time.sleep(1)

            self._print_statistics()

        except socket.error as e:
            print(f"Error: Socket error occurred: {e}")
            if self.is_ipv6:
                print("Falling back to IPv4 if possible...")
                self.is_ipv6 = False
                self.ping()  # Retry with IPv4
        except PermissionError:
            print("Error: This program requires root privileges")
            print("Run with: sudo python3 main.py <target>")
        except socket.gaierror as e:
            print(f"Error: Could not resolve hostname {self.target}: {e}")
        except ValueError as e:
            print(f"Error: {str(e)}")
        except Exception as e:
            print(f"Error: Unexpected error: {str(e)}")
        finally:
            try:
                sock.close()
            except:
                pass

    def _is_valid_ip(self, address):
        try:
            socket.inet_pton(socket.AF_INET6 if self.is_ipv6 else socket.AF_INET, address)
            return True
        except socket.error:
            return False

    def _process_reply(self, reply, expected_seq, expected_id):
        try:
            if self.is_ipv6:
                icmp_header = reply[0:8]
            else:
                ip_header = reply[0:20]
                iph = struct.unpack('!BBHHHBBH4s4s', ip_header)
                ip_header_len = (iph[0] & 0xF) * 4
                icmp_header = reply[ip_header_len:ip_header_len + 8]

            type_, code, checksum, packet_id, sequence = struct.unpack('!BBHHH', icmp_header)
            expected_type = 129 if self.is_ipv6 else 0
            
            if type_ != expected_type:
                return False
            return packet_id == expected_id and sequence == expected_seq
        except Exception as e:
            print(f"Error processing reply: {e}")
            return False

    def _print_statistics(self):
        if self.sent > 0:
            print(f"\n--- {self.target} ping statistics ---")
            loss = ((self.sent - self.received) / self.sent) * 100
            print(f"{self.sent} packets transmitted, {self.received} received, {loss:.0f}% packet loss")
            if self.received > 0:
                print(f"rtt min/avg/max = {min(self.rtt_list):.3f}/{sum(self.rtt_list)/len(self.rtt_list):.3f}/{max(self.rtt_list):.3f} ms")

def main():
    parser = argparse.ArgumentParser(description="Custom Ping Utility with IPv4 and IPv6 support")
    parser.add_argument("target", help="Target hostname or IP address (IPv4 or IPv6)")
    parser.add_argument("-c", "--count", type=int, default=4, help="Number of pings")
    parser.add_argument("-t", "--ttl", type=int, default=64, help="Time to live (hop limit)")
    parser.add_argument("-W", "--timeout", type=int, default=2, help="Timeout in seconds")
    
    args = parser.parse_args()
    
    ping = PingUtility(
        target=args.target,
        count=args.count,
        ttl=args.ttl,
        timeout=args.timeout
    )
    ping.ping()

if __name__ == "__main__":
    main()
