ifneq ("","$(wildcard /etc/lsb-release)")
DLSE_OS_NAME:=$(shell lsb_release -si)
DLSE_OS_ARCH:=$(shell uname -m | sed 's/x86_//;s/i[3-6]86/32/')
DLSE_OS_VERSION:=$(shell lsb_release -sr)

ifeq ($(DLSE_OS_ARCH),64)
ifeq ($(DLSE_OS_VERSION),16.04)
DLSE_OS_SUPPORTED:=1
else
DLSE_OS_SUPPORTED:=0
endif
else
DLSE_OS_SUPPORTED:=0
endif

else
DLSE_OS_SUPPORTED:=0
endif


