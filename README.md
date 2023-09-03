# DREAMPlace-Docker
Enrich the functionality of DREAMPlace's docker build


# How to build

```bash
./build.sh
```

# Run the docker with exposing ssh port
```
./run.sh
```

# Example of ~/.ssh/config
Host 4090pc-nat-dreamplace
	HostName 192.168.1.1 #your host ip
	User root
	Port 9022
	IdentityFile ~/.ssh/ssh_key_busydocker 
	ForwardX11 yes
	ForwardX11Timeout 0
