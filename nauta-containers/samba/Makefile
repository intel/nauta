all: build

build:
	docker build --build-arg http_proxy=${http_proxy} --build-arg https_proxy=${https_proxy} -t nauta-samba .
	
push:
	docker tag nauta-samba my-little-registry.pl/nauta-samba
	docker push my-little-registry.pl/nauta-samba
	
deps:
	sudo apt install cifs-utils samba-client

local_run: local_halt
	docker run --rm -p 139:139 -p 445:445 --name nauta-samba nauta-samba
	
local_bash:
	docker exec -ti nauta-samba /bin/bash
	
local_run_bg: local_halt
	docker run --rm -p 139:139 -p 445:445 -d --name nauta-samba nauta-samba
	
local_halt:
	docker stop nauta-samba || true
	docker rm nauta-samba || true
	
#local_mkuser:
#	docker exec -ti nauta-samba adduser $(U)
#	docker exec -ti nauta-samba bash -c "( echo $(P) ; echo $(P); ) | smbpasswd -a $(U) "

local_mkuser_uid:
	docker exec -ti nauta-samba groupadd -g $(GROUPID) $(U)
	docker exec -ti nauta-samba adduser --uid $(USERID) --gid $(GROUPID) $(U)
	docker exec -ti nauta-samba bash -c "( echo $(P) ; echo $(P); ) | smbpasswd -a $(U) "	
	
local_mount:
	mkdir -p $(U)
	sudo mount -t cifs -o username=$(U),password=$(P),rw,uid=$(shell id -u)  //127.0.0.1/$(U) $(shell pwd)/$(U)

local_mount_public:
	mkdir -p shared
	sudo mount -t cifs -o username=$(U),password=$(P),rw,uid=$(shell id -u)  //127.0.0.1/shared $(shell pwd)/shared
	
local_test: build local_run_bg
	sleep 10
	sudo umount ./foo || true
	sudo umount ./shared || true
	U=foo P=bar USERID=10015 GROUPID=20015 make local_mkuser_uid
	U=foo P=bar make local_mount
	echo "ok" > ./foo/test_foo
	smbclient -U foo //127.0.0.1/foo bar -c=ls | grep test_foo
	U=foo P=bar make local_mount_public
	echo "ok" > ./shared/test_shared
	smbclient -U foo //127.0.0.1/shared bar -c=ls | grep test_shared
	
local_test_auto: build local_run_bg
	sleep 10
	sudo umount ./user_u1 || true
	sudo umount ./user_u2 || true
	sudo umount ./shared || true
	
	docker exec -ti nauta-samba bash -c "echo 'haslo' > /etc/secrets/samba-users/10001_20001_u1"
	sleep 10
	mkdir -p ./user_u1
	sudo mount -t cifs -o username=user_u1,password=haslo,rw,uid=$(shell id -u)  //127.0.0.1/user_u1 $(shell pwd)/user_u1
	echo "works" > ./user_u1/test_u1
	smbclient -U user_u1 //127.0.0.1/user_u1 haslo -c=ls | grep test_u1
	
	mkdir -p ./shared
	sudo mount -t cifs -o username=user_u1,password=haslo,rw,uid=$(shell id -u)  //127.0.0.1/shared $(shell pwd)/shared
	echo "works" > ./shared/test_u1_shared
	smbclient -U user_u1 //127.0.0.1/shared haslo -c=ls | grep test_u1_shared
	
	docker exec -ti nauta-samba bash -c "echo 'haslo2' > /etc/secrets/samba-users/10002_20002_u2"
	sleep 10
	mkdir -p ./user_u2
	sudo mount -t cifs -o username=user_u2,password=haslo2,rw,uid=$(shell id -u)  //127.0.0.1/user_u2 $(shell pwd)/user_u2
	echo "works" > ./user_u2/test_u2
	smbclient -U user_u2 //127.0.0.1/user_u2 haslo2 -c=ls | grep test_u2	
	
	#U=foo P=bar USERID=10015 GROUPID=20015 make local_mkuser_uid
	#U=foo P=bar make local_mount
	#echo "ok" > ./foo/test_foo
	#smbclient -U foo //127.0.0.1/foo bar -c=ls | grep test_foo
	#U=foo P=bar make local_mount_public
	#echo "ok" > ./shared/test_shared
	#smbclient -U foo //127.0.0.1/shared bar -c=ls | grep test_shared
	
	
	
