#!/bin/bash

echo "Testing ping utility..."
echo "Running on $(date)"
echo "Python version: $(python3 --version)"

# Test 1: Basic IPv4 ping to localhost
echo -e "\n------------------------\n"
echo "Test 1: Pinging localhost (IPv4)"
sudo python3 src/main.py 127.0.0.1 -c 4

# Test 2: IPv4 ping with custom TTL
echo -e "\n------------------------\n"
echo "Test 2: Pinging google.com (IPv4) with TTL 30"
sudo python3 src/main.py google.com -c 4 -t 30

# Test 3: IPv4 ping with custom timeout
echo -e "\n------------------------\n"
echo "Test 3: Pinging 8.8.8.8 (IPv4) with 1s timeout"
sudo python3 src/main.py 8.8.8.8 -c 4 -W 1

# Test 4: Basic IPv6 ping to localhost
echo -e "\n------------------------\n"
echo "Test 4: Pinging ::1 (IPv6 loopback)"
sudo python3 src/main.py ::1 -c 4

# Test 5: IPv6 ping with custom TTL and timeout
echo -e "\n------------------------\n"
echo "Test 5: Pinging ::1 (IPv6) with TTL 20 and 1s timeout"
sudo python3 src/main.py ::1 -c 4 -t 20 -W 1

echo -e "\n------------------------\n"
echo "Testing complete."
