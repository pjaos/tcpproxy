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

## Help
Help text is available on the command line.

```
tcpproxy -h
usage: tcpproxy.py [-h] [-c] [-u USER] [-e] [-d] [-s] [--debug]

This program provides a simple proxy server.

optional arguments:
  -h, --help            show this help message and exit
  -c, --config          Configure the TCP proxy server.
  -u USER, --user USER  Set the user for auto start.
  -e, --enable_auto_start
                        Enable auto start this program when this computer starts.
  -d, --disable_auto_start
                        Disable auto start this program when this computer starts.
  -s, --check_status    Check the status of an auto started tcpproxy instance.
  --debug               Enable debugging.
```

## Configuration
The persistent configuration can be configured from the interface shown below if the -c/--config command line option is used.

```
tcpproxy -c
INFO:  *****************************************************************************
INFO:  | ID  | Bind Address | Listen Port | Destination Address | Destination Port |
INFO:  *****************************************************************************
INFO:  | 1   | 0.0.0.0/32   | 2222        | localhost           | 22               !
INFO:  | 2   | 0.0.0.0/32   | 3333        | localhost           | 22               !
INFO:  *****************************************************************************
INPUT: A: Add, E: Edit, D: Delete, S: Save or Q: to quit.: 
```

## Run normally

- An example running the tool with the above configuration.

```
tcpproxy
INFO:  Forwarding 0.0.0.0/32:2222 to localhost:22
INFO:  Forwarding 0.0.0.0/32:3333 to localhost:22
```

As clients connect to the TCP proxy server they are displayed as shown below.

E.G

```
INFO:  Connected 0.0.0.0:2222 to localhost:22
```

## Configuring auto start.
It is possible to start the server on Linux systems that support systemd. This is
done using the following arguments.

```
  -u USER, --user USER  Set the user for auto start.
  -e, --enable_auto_start
                        Enable auto start this program when this computer starts.
  -d, --disable_auto_start
                        Disable auto start this program when this computer starts.
  -s, --check_status    Check the status of an auto started tcpproxy instance.
```

- Enable auto start

E.G

```
sudo tcpproxy -e --user USERNAME 
INFO:  Enabled auto start  
```

Where USERNAME is your Linux username.

- Check the auto start status

```
sudo tcpproxy -s
INFO:  ● tcpproxy.service
INFO:       Loaded: loaded (/etc/systemd/system/tcpproxy.service; enabled; vendor preset: enabled)
INFO:       Active: active (running) since Sun 2022-03-27 08:05:40 BST; 1min 27s ago
INFO:     Main PID: 27890 (tcpproxy)
INFO:        Tasks: 4 (limit: 18993)
INFO:       Memory: 7.5M
INFO:       CGroup: /system.slice/tcpproxy.service
INFO:               ├─27890 /bin/sh /usr/local/bin/tcpproxy
INFO:               └─27891 python3 /usr/local/bin/python-tcpproxy.pipenvpkg/tcpproxy.py
INFO:  
INFO:  Mar 27 08:05:40 E5570 systemd[1]: Started tcpproxy.service.
INFO:  
INFO:  
```

- Disable auto start

```
sudo tcpproxy -d
INFO:  Disabled auto start
```

