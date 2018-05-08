ifeq ($(OS),Windows_NT)
DETECTED_OS:=Windows
else
DETECTED_OS:=$(shell uname -s)
endif

ifeq ($(DETECTED_OS),Linux)
DLSE_OS:=Linux
include $(LIBS_DIRECTORY)/linux-detect.mk
else ifeq ($(DETECTED_OS),Darwin)
DLSE_OS:=Darwin
DLSE_OS_SUPPORTED:=0
else ifeq ($(DETECTED_OS),Windows)
DLSE_OS:=Windows
DLSE_OS_SUPPORTED:=0
else
DLSE_OS:=Unknown
DLSE_OS_SUPPORTED:=0
endif
