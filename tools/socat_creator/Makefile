# Copyright (c) 2018, Intel Corporation

# Redistribution and use in source and binary forms, with or without modification,
# are permitted provided that the following conditions are met:
#     * Redistributions of source code must retain the above copyright notice,
#       this list of conditions and the following disclaimer.
#     * Redistributions in binary form must reproduce the above copyright notice,
#       this list of conditions and the following disclaimer in the documentation
#       and/or other materials provided with the distribution.

# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS" AND
# ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE
# DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT OWNER OR CONTRIBUTORS BE LIABLE FOR
# ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES
# (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES;
# LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON
# ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT
# (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS
# SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.

create:
	@rm -f final centos-docker-socat.tar.xz centos-docker-socat.tar.gz
	@docker build -t socat-image:latest -f Dockerfile.socat .
	@echo "image built"
	@docker run --name socat_image_creator socat-image:latest bash -c "tar cvpJfh socat-container-image.tar.xz /usr/bin/socat_script.sh /usr/bin/dig /usr/bin/cat /bin/bash /bin/ps /bin/ls /lib64/libwrap.so.0 /lib64/librt.so.1 /lib64/libutil.so.1 /lib64/libreadline.so.6 /lib64/libssl.so.10 /lib64/libcrypto.so.10 /lib64/libc.so.6 /lib64/libnsl.so.1 /lib64/libpthread.so.0 /lib64/libtinfo.so.5 /lib64/libgssapi_krb5.so.2 /lib64/libkrb5.so.3 /lib64/libcom_err.so.2 /lib64/libk5crypto.so.3 /lib64/libdl.so.2 /lib64/libz.so.1 /lib64/libkrb5support.so.0 /lib64/ld-linux-x86-64.so.2 /lib64/libkeyutils.so.1 /lib64/libresolv.so.2 /lib64/libselinux.so.1 /lib64/libpcre.so.1 /lib64/libcap.so.2 /lib64/libacl.so.1 /lib64/libattr.so.1 /lib64/libprocps.so.4 /lib64/libsystemd.so.0 /lib64/libm.so.6 /lib64/liblzma.so.5 /lib64/liblz4.so.1 /lib64/libgcrypt.so.11 /lib64/libgpg-error.so.0 /lib64/libdw.so.1 /lib64/libgcc_s.so.1 /lib64/libelf.so.1 /lib64/libbz2.so.1 /lib64/libdns.so.100 /lib64/liblwres.so.90 /lib64/libbind9.so.90 /lib64/libisccfg.so.90 /lib64/libisccc.so.90 /lib64/libisc.so.95 /lib64/libGeoIP.so.1 /lib64/libxml2.so.2 /lib64/libidn.so.11 /usr/bin/socat /etc/resolv.conf; touch final; sleep 10000" & > /dev/null 2>&1
	@echo "container started"
	@while ! test -f "final"; do \
		sleep 2 ; \
		echo "Still waiting" ; \
		docker cp socat_image_creator:/final . ; \
	done
	docker cp socat_image_creator:/socat-container-image.tar.xz .
	@docker build -t socat-container-image:latest -f Dockerfile.final .
	@docker save socat-container-image:latest -o socat-container-image.tar.gz
	#removing all artifacts
	@docker container kill socat_image_creator
	@docker rm socat_image_creator
	@docker rmi socat-image:latest
	@rm -f final socat-container-image.tar.xz

