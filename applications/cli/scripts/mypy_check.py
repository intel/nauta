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

import argparse
import subprocess
from typing import List


IGNORED_ERRORS = {
    'Unexpected keyword argument "alias" for "command"',
    '"command" defined here',
}


def run_mypy_check(target: str, config_file: str) -> List[str]:
    try:
        result = subprocess.run(['mypy', '--config-file', config_file, target], stdout=subprocess.PIPE)
        errors = result.stdout.decode('utf-8').split('\n')
        errors = [e for e in errors if e]  # Clear empty errors
        return errors
    except subprocess.CalledProcessError as e:
        print(e.output)
        raise


def filter_mypy_results(mypy_results: List[str]) -> List[str]:
    return [error for error in mypy_results 
            if not any(ignored_error in error for ignored_error in IGNORED_ERRORS)]


def parse_args():
    parser = argparse.ArgumentParser(description='A simple wrapper for mypy that allows ignoring specific types for errors.')
    parser.add_argument('--config-file', default='mypy.ini', help='Path to mypy config file.')
    parser.add_argument('--target', default='main.py', help='Path to mypy target file.')
    return parser.parse_args()


if __name__ == "__main__":
    args = parse_args()
    mypy_results = run_mypy_check(target=args.target, config_file=args.config_file)
    filtered_mypy_results = filter_mypy_results(mypy_results)
    if filtered_mypy_results:
        print('Mypy check failed.')
        print(filtered_mypy_results)
        print('\n'.join(filtered_mypy_results))
        exit(1)
    else:
        print('Mypy check passed successfully.')
        exit(0)
