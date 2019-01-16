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

DOCKER_IMAGE_NAME := nauta-gui
DOCKER_EXTERNAL_PORT := 9000

install:
	@npm install

build:	install
	@npm run build

style:	install
	@npm run lint

test:	install style
	@npm run test

run-dev:	install
	@npm run start-dev

run-prod:	install	build
	@npm run start-prod

docker-build:	install	build
	@docker build -t $(DOCKER_IMAGE_NAME) .

docker-run:	docker-build
	@docker run -d -p $(DOCKER_EXTERNAL_PORT):9000 --name=$(DOCKER_IMAGE_NAME) $(DOCKER_IMAGE_NAME)

docker-stop-rm:
	@docker stop $(DOCKER_IMAGE_NAME)
	@docker rm $(DOCKER_IMAGE_NAME)
