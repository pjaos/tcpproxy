# tcpproxy
A simple TCP proxy server.

This can be installed via pip or via the deb package (onto debian based Linux systems).

# Installation

- Install via pip

```
pip install .
```

- Install using debian package

```
E.G
sudo dpkg -i packages/python-tcpproxy-1.0-all.deb
```

# Usage

## Configure
- The persistent configuration can be configured from the interface shown below.

tcpproxy -c
INFO:  *****************************************************************************
INFO:  | ID  | Bind Address | Listen Port | Destination Address | Destination Port |
INFO:  *****************************************************************************
INFO:  | 1   | 0.0.0.0/32   | 2222        | localhost           | 22               !
INFO:  | 2   | 0.0.0.0/32   | 3333        | localhost           | 22               !
INFO:  *****************************************************************************
INPUT: A: Add, E: Edit, D: Delete, S: Save or Q: to quit.: 

## Run normally

- An example running the tool followed by a tcp proxy connection being made.

```
tcpproxy
INFO:  Connected 0.0.0.0:2222 to localhost:22
```


