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

import subprocess
import errno
import datetime
from distutils.version import LooseVersion

import pytest


from util.system import execute_system_command, check_port_availability, format_timestamp_for_cli, handle_error, \
    get_os_version, get_windows_edition, WINDOWS_EDITIONS, ExternalCliClient, ExternalCliCommand, \
    format_duration_for_cli


def test_execute_system_command(mocker):
    mocker.patch('subprocess.check_output')
    output, exit_code, log_output = execute_system_command(['ls'])

    # noinspection PyUnresolvedReferences
    assert subprocess.check_output.call_count == 1


def test_execute_system_command_known_error(mocker):

    bad_exit_code = 1

    # noinspection PyUnusedLocal
    def raise_command_exception(*args, **kwargs):
        raise subprocess.CalledProcessError(returncode=bad_exit_code, cmd='ls')

    mocker.patch('subprocess.check_output', new=raise_command_exception)

    output, exit_code, log_output = execute_system_command(['ls'])

    assert exit_code == bad_exit_code


def test_execute_system_command_unknown_error(mocker):

    # noinspection PyUnusedLocal
    def raise_command_exception(*args, **kwargs):
        raise subprocess.SubprocessError()

    mocker.patch('subprocess.check_output', new=raise_command_exception)

    with pytest.raises(subprocess.SubprocessError):
        execute_system_command(['ls'])


def test_check_port_availability_success(mocker):
    mocker.patch("socket.socket")
    assert check_port_availability(9000)


def test_check_port_availability_failure(mocker):
    socket_local = mocker.patch("socket.socket.bind")
    socket_local.side_effect = OSError()

    with pytest.raises(RuntimeError):
        check_port_availability(9000)


def test_check_port_availability_occupied(mocker):
    socket_local = mocker.patch("socket.socket.bind")
    socket_local.side_effect = OSError(errno.EADDRINUSE, "Address in use")

    assert not check_port_availability(9000)


def test_format_timestamp_for_cli(mocker):
    tzlocal_mock = mocker.patch("dateutil.tz.tzlocal")
    tzlocal_mock.return_value = datetime.timezone(datetime.timedelta(hours=1))

    cli_timestamp = format_timestamp_for_cli("2018-10-11T20:30:30Z")

    assert cli_timestamp == "2018-10-11 09:30:30 PM"


def test_format_duration_for_cli():
    start_date = datetime.datetime(year=2019, month=1, day=2, hour=3, minute=34, second=42)
    end_date = datetime.datetime(year=2019, month=1, day=4, hour=1, minute=22, second=51)
    timedelta = end_date - start_date
    expected_string = "1d 21h 48m 9s"
    assert format_duration_for_cli(timedelta) == expected_string


def test_handle_error_no_logger(mocker):
    click_echo_mock = mocker.patch("click.echo")

    try:
        handle_error(log_msg="", user_msg="")
    except Exception:
        pytest.fail("Handle error should not allow None logger to call logger.exception.")

    assert click_echo_mock.call_count == 1


def test_handle_error_no_log_msg(mocker):
    click_echo_mock = mocker.patch("click.echo")
    logger = mocker.MagicMock(exception=lambda msg: None)
    mocker.spy(logger, "exception")

    handle_error(logger=logger, user_msg="")

    assert logger.exception.call_count == 0
    assert click_echo_mock.call_count == 1


def test_handle_error_no_user_msg(mocker):
    click_echo_mock = mocker.patch("click.echo")
    logger = mocker.MagicMock(exception=lambda msg: None)
    mocker.spy(logger, "exception")

    handle_error(logger=logger, log_msg="")

    assert logger.exception.call_count == 1
    assert click_echo_mock.call_count == 0


def test_handle_error_no_exit(mocker):
    click_echo_mock = mocker.patch("click.echo")
    logger = mocker.MagicMock(exception=lambda msg: None)
    mocker.spy(logger, "exception")

    handle_error(logger=logger, log_msg="", user_msg="")

    assert logger.exception.call_count == 1
    assert click_echo_mock.call_count == 1


def test_get_os_version_windows_10(mocker):
    system_mock = mocker.patch("util.system.platform.system")
    system_mock.return_value = "Windows"
    release_mock = mocker.patch("util.system.platform.release")
    release_mock.return_value = "10"
    get_windows_edition_mock = mocker.patch("util.system.get_windows_edition")
    get_windows_edition_mock.return_value = "pro"
    os_name, os_version = get_os_version()

    assert os_name == "windows_pro"
    assert os_version == LooseVersion("10")
    assert get_windows_edition_mock.call_count == 1


def test_get_os_version_windows_not_10(mocker):
    system_mock = mocker.patch("util.system.platform.system")
    system_mock.return_value = "Windows"
    release_mock = mocker.patch("util.system.platform.release")
    release_mock.return_value = "8"
    get_windows_edition_mock = mocker.patch("util.system.get_windows_edition")
    os_name, os_version = get_os_version()

    assert os_name == "windows"
    assert os_version == LooseVersion("8")
    assert get_windows_edition_mock.call_count == 0


def test_get_windows_edition(mocker):
    execute_system_command_mock = mocker.patch("util.system.execute_system_command")
    execute_system_command_mock.return_value = "4", 0, "4"

    windows_edition = get_windows_edition()

    assert windows_edition == WINDOWS_EDITIONS[4]


def test_get_os_version_macos(mocker):
    system_mock = mocker.patch("util.system.platform.system")
    system_mock.return_value = "Darwin"
    mac_ver_mock = mocker.patch("util.system.platform.mac_ver")
    mac_ver_mock.return_value = ("10.0.13", )
    os_name, os_version = get_os_version()

    assert os_name == "macos"
    assert os_version == LooseVersion("10.0.13")


def test_get_os_version_debian(mocker):
    system_mock = mocker.patch("util.system.platform.system")
    system_mock.return_value = "Linux"
    read_os_release_mock = mocker.patch("util.system.distro.info")
    read_os_release_mock.return_value = {"id": "debian", "version": "9.3"}
    os_name, os_version = get_os_version()

    assert os_name == "debian"
    assert os_version == LooseVersion("9.3")


def test_get_os_version_empty(mocker):
    system_mock = mocker.patch("util.system.platform.system")
    system_mock.return_value = "abc"
    os_name, os_version = get_os_version()

    assert os_name == ""
    assert os_version == LooseVersion("0")


def test_execute_system_command_limited_logs(mocker):
    cop_mock = mocker.patch('subprocess.check_output')
    cop_mock.return_value = 50*"a"
    output, exit_code, log_output = execute_system_command(['ls'], logs_size=20)

    assert len(log_output) == 20
    assert len(output) == 50
    # noinspection PyUnresolvedReferences
    assert subprocess.check_output.call_count == 1


def test_external_cli_client(mocker):
    command_mock = mocker.patch('util.system.ExternalCliCommand')
    client = ExternalCliClient(executable='test')
    client.fake_command()

    assert command_mock.called_with(cmd=['test', 'fake_command'])


def test_external_cli_command(mocker):
    exec_mock = mocker.patch('util.system.execute_system_command')
    exec_mock.return_value = '', 0, ''
    cmd = ExternalCliCommand(cmd=['foo', 'bar'])
    cmd('arg-1', long_parameter='bla')

    assert exec_mock.called_with(cmd=['foo', 'bar', 'arg-1', '--long-parameter', 'bla'])


def test_external_cli_command_flags(mocker):
    exec_mock = mocker.patch('util.system.execute_system_command')
    exec_mock.return_value = '', 0, ''
    cmd = ExternalCliCommand(cmd=['foo', 'bar'])
    cmd('arg-1', flag=True, unset_flag=False)

    assert exec_mock.called_with(cmd=['foo', 'bar', 'arg-1', '--flag'])
