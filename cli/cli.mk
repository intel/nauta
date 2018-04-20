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


build: $(ACTIVATE)
	@. $(ACTIVATE); pip install pyinstaller;

ifeq (Windows,$(OS))
	@. $(ACTIVATE); pyinstaller --paths "C:\Program Files (x86)\Windows Kits\10\Redist\ucrt\DLLs\x64" -F main.py;
	@wget https://ftp.nervana.sclab.intel.com/public/draft-bundles/windows/draft-v0.13.0-windows-amd64.tar.gz --no-check-certificate -O draft.tar.gz
endif

ifeq (Linux,$(OS))
	@. $(ACTIVATE); pyinstaller -F main.py;
	@wget https://ftp.nervana.sclab.intel.com/public/draft-bundles/linux/draft-v0.13.0-linux-amd64.tar.gz --no-check-certificate -O draft.tar.gz
endif
	@tar -zxf draft.tar.gz -C dist
	@rm -f draft.tar.gz
	@cp -Rf draft/packs/* dist/.draft/packs/


style: $(DEV_VIRTUALENV_MARK)
	@. $(ACTIVATE); flake8 draft/ util/ main.py

test: $(DEV_VIRTUALENV_MARK)
	@. $(ACTIVATE); py.test

cli-check: venv-dev test style
