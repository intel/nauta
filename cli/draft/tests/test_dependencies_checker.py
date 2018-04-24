#
# INTEL CONFIDENTIAL
# Copyright (c) 2018 Intel Corporation
#
# The source code contained or described herein and all documents related to
# the source code ("Material") are owned by Intel Corporation or its suppliers
# or licensors. Title to the Material remains with Intel Corporation or its
# suppliers and licensors. The Material contains trade secrets and proprietary
# and confidential information of Intel or its suppliers and licensors. The
# Material is protected by worldwide copyright and trade secret laws and treaty
# provisions. No part of the Material may be used, copied, reproduced, modified,
# published, uploaded, posted, transmitted, distributed, or disclosed in any way
# without Intel's prior express written permission.
#
# No license under any patent, copyright, trade secret or other intellectual
# property right is granted to or conferred upon you by disclosure or delivery
# of the Materials, either expressly, by implication, inducement, estoppel or
# otherwise. Any license under such intellectual property rights must be express
# and approved by Intel in writing.
#

from copy import deepcopy

from pytest import fixture, raises

from draft import dependencies_checker

version_returns = {
    'kubectl': ('Client Version: version.Info{Major:"1", Minor:"10", GitVersion:"v1.10.0", '
                'GitCommit:"fc32d2f3698e36b93322a3465f63a14e9f0eaead", GitTreeState:"clean", '
                'BuildDate:"2018-03-26T16:55:54Z", GoVersion:"go1.9.3", Compiler:"gc", Platform:"linux/amd64"}', 0),
    'helm': ('Client: &version.Version{SemVer:"v2.8.2", '
             'GitCommit:"a80231648a1473929271764b920a8e346f6de844", GitTreeState:"clean"}', 0),
    'docker': ("""Client:
 Version:       18.03.0-ce
 API version:   1.37
 Go version:    go1.9.4
 Git commit:    0520e24
 Built: Wed Mar 21 23:10:09 2018
 OS/Arch:       linux/amd64
 Experimental:  false
 Orchestrator:  swarm

Server:
 Engine:
  Version:      18.03.0-ce
  API version:  1.37 (minimum version 1.12)
  Go version:   go1.9.4
  Git commit:   0520e24
  Built:        Wed Mar 21 23:08:36 2018
  OS/Arch:      linux/amd64
  Experimental: false
', 0
""", 0),
    'draft': ('&version.Version{SemVer:"canary", GitCommit:"78385afe65500ebb4f546341f229a5f200f1128a", '
              'GitTreeState:"clean"}', 0)
}

original_version_returns = deepcopy(version_returns)


def revert_version_returns():
    global version_returns
    version_returns = deepcopy(original_version_returns)


@fixture
def dependencies_checker_mocked(mocker):
    mocker.patch.object(dependencies_checker, 'execute_system_command',
                        new=lambda cmd, *args, **kwargs: version_returns[cmd[0]])
    mocker.patch.object(dependencies_checker, 'call_draft', new=lambda *args, **kwargs: version_returns['draft'])

    return dependencies_checker


# noinspection PyShadowingNames
def test_check(dependencies_checker_mocked):

    dependencies_checker_mocked.check()


# noinspection PyShadowingNames
def test_check_bad_version(dependencies_checker_mocked):
    version_returns['helm'] = ('Client: &version.Version{SemVer:"v2.8.2", '
                               'GitCommit:"fc32d2f3698e36b93322a3465f63a14e9f0eaead", GitTreeState:"clean"}', 0)

    dependencies_checker_mocked.check()

    revert_version_returns()


# noinspection PyShadowingNames
def test_check_no_command(dependencies_checker_mocked: dependencies_checker):
    version_returns['docker'] = ('command not found', 127)

    dependencies_checker_mocked.check()

    revert_version_returns()


# noinspection PyShadowingNames
def test_check_bad_command_output(dependencies_checker_mocked):
    version_returns['draft'] = ('&version.Version{SemVer:"canary", GitTreeState:"clean"}', 0)
    with raises(RuntimeError):
        dependencies_checker_mocked.check()

    revert_version_returns()


# noinspection PyShadowingNames
def test_docker_client_server_version_mismatch(dependencies_checker_mocked):
    version_returns['docker'] = ("""Client:
 Version:       18.03.0-ce
 API version:   1.37
 Go version:    go1.9.4
 Git commit:    0520e24
 Built: Wed Mar 21 23:10:09 2018
 OS/Arch:       linux/amd64
 Experimental:  false
 Orchestrator:  swarm

Server:
 Engine:
  Version:      17.04.1-ce
  API version:  1.37 (minimum version 1.12)
  Go version:   go1.9.4
  Git commit:   0520e24
  Built:        Wed Mar 21 23:08:36 2018
  OS/Arch:      linux/amd64
  Experimental: false
', 0
""", 0)

    dependencies_checker_mocked.check()

    revert_version_returns()
