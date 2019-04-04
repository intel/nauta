#
# Copyright (c) 2019 Intel Corporation
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#

import os
import subprocess
import sys
import time

if len(sys.argv) < 2:
    raise RuntimeError("please provide at least 1 argument")

main_process = subprocess.Popen(["python", *sys.argv[1:]], stdout=sys.stdout, stderr=sys.stderr)

while True:
    if os.path.isfile("/pod-data/END"):
        main_process.kill()
        sys.exit(0)

    main_process_exit_code = main_process.poll()
    if main_process.poll() is not None:
        sys.exit(main_process_exit_code)

    time.sleep(1)
