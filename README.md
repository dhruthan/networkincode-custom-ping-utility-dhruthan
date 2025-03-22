# Custom Ping Utility

A Python-based ping utility that supports both IPv4 and IPv6, allowing users to send ICMP Echo Requests and receive Echo Replies with customizable options such as TTL (hop limit) and timeout.

## Features
- Supports IPv4 and IPv6 addresses.
- Customizable packet count, TTL/hop limit, and timeout.
- Detailed debugging output for troubleshooting.
- Falls back to IPv4 if IPv6 is unavailable (for hostnames).
- Command-line interface with argparse for easy usage.

## Requirements
- Python 3.6+ (tested with Python 3.10.12 on Ubuntu 22.04.5 LTS).
- Root privileges (`sudo`) for raw socket access.
- IPv6 kernel support enabled (`cat /proc/sys/net/ipv6/conf/all/disable_ipv6` should be `0`).

## Steps to run

1. **Clone this repo and Navigate to directory**
      
2. **Execute the Test file**
   ```sh
   sudo ./scripts/test.sh
   ``` 

## Usage   

python3 ./src/main.py [-h] [-c COUNT] [-t TTL] [-W TIMEOUT] target

positional arguments:
  target                Target hostname or IP address (IPv4 or IPv6)

  options:
  -h, --help            show this help message and exit
  -c COUNT, --count COUNT
                        Number of pings (default: 4)
  -t TTL, --ttl TTL     Time to live/hop limit (default: 64)
  -W TIMEOUT, --timeout TIMEOUT
                        Timeout in seconds (default: 2)
