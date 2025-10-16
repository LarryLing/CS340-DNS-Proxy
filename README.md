# CS340 Project 1

## Instructions

### 1. Virtual Environment

Ensure you are running this project from within a virtual environment

```sh
python -m venv .venv

source .venv/bin/activate
```

Install the libraries from `requirements.txt`

```sh
pip install -r requirements.txt
```

### 2. Starting The Proxy

Run the following command to start the proxy for part 1

```sh
python3 part1/part1.py
```

Run the following command to start the proxy for part 2

```sh
python3 part2/part2.py
```

### 3. Querying The Proxy

Run the following commands to test the proxies

```sh
dig @127.0.0.1 -p 1053 example.com A

dig @127.0.0.1 -p 1053 google.com A
```

### 4. Logging

The logs in JSON format can be found in `dns_log.json` files in the respective folders. They will be written to after the proxy process has been terminated.

## Acknowledgements

- [struct](https://docs.python.org/3/library/struct.html)
- [asyncio](https://docs.python.org/3/library/asyncio.html)
- [socket](https://docs.python.org/3/library/socket.html)
- [dnslib](https://pypi.org/project/dnslib/)
