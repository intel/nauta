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

import platform

from click.testing import CliRunner

from commands.mount import get_mount_command_linux, get_mount_command_windows, get_mount_command_osx, mount, \
    get_unmount_command_linux, get_unmount_command_windows, get_unmount_command_osx, get_mounts_windows, \
    get_mounts_linux_osx

from cli_text_consts import MountCmdTexts as Texts


TEST_USR = "test_user"
TEST_PSW = "test_password"
TEST_ADR = "test_address"

CORRECT_LINUX_MOUNT = f"sudo mount.cifs -o username={TEST_USR},password=" \
                      f"{TEST_PSW},rw,uid=10001 //{TEST_ADR}/<NAUTA_FOLDER> <MOUNTPOINT>"
CORRECT_LINUX_UNMOUNT = "sudo umount <MOUNTPOINT> [-fl]"

CORRECT_WINDOWS_MOUNT = f"net use <MOUNTPOINT> \\\\{TEST_ADR}\\<NAUTA_FOLDER> /user:{TEST_USR} {TEST_PSW}"
CORRECT_WINDOWS_UNMOUNT = "net use <MOUNTPOINT> /d"

CORRECT_OSX_MOUNT = f"mount_smbfs //'{TEST_USR}:{TEST_PSW}'@{TEST_ADR}/<NAUTA_FOLDER> <MOUNTPOINT>"
CORRECT_OSX_UNMOUNT = "umount <MOUNTPOINT> [-f]"

MOUNT_IP = "1.2.3.4"

WIN_NET_USE_OUTPUT = f"Status       Local     Remote                    Network \n " \
                     f"-------------------------------------------------------------------------------\n" \
                     f"Disconnected S:        \\\\{MOUNT_IP}\input\n" \
                                                "Microsoft Windows Network\n" \
                     f"Disconnected Z:        \\\\{MOUNT_IP}\input\n" \
                                                "Microsoft Windows Network\n" \
                     "Disconnected X:        \\\\1.1.1.1\input\n" \
                                                "Microsoft Windows Network\n" \
                     f"Disconnected           \\\\{MOUNT_IP}\input\n" \
                                                "Microsoft Windows Network\n" \
                     f"Disconnected           \\\\{MOUNT_IP}\output\n" \
                                                "Microsoft Windows Network\n" \
                     f"The command completed successfully."


LINUX_MOUNT_OUTPUT = "freezer on /run/lxcfs/controllers/freezer type cgroup (rw,relatime,freezer)\n" \
                     "name=systemd on /run/lxcfs/controllers/name=systemd type cgroup (rw,relatime,xattr," \
                     "release_agent=/lib/systemd/systemd-cgroups-agent,name=systemd)\n" \
                     "lxcfs on /var/lib/lxcfs type fuse.lxcfs (rw,nosuid,nodev,relatime,user_id=0," \
                     "group_id=0,allow_other)\n" \
                     f"//{MOUNT_IP}/input on /home/username/input type cifs " \
                     "(rw,relatime,vers=1.0,cache=strict,username=username,domain=NAUTA-SAMBA-6DBF869D46" \
                     "-7SNF6,uid=10001,forceuid,gid=0,noforcegid,addr=10.91.120.87,unix,posixpaths," \
                     "serverino,mapposix,acl,rsize=1048576,wsize=65536,actimeo=1)\n" \
                     f"//{MOUNT_IP}/input on /home/username/input type cifs " \
                     "(rw,relatime,vers=1.0,cache=strict,username=username2,domain=NAUTA-SAMBA-6DBF869D46" \
                     "-7SNF6,uid=10001,forceuid,gid=0,noforcegid,addr=10.91.120.87,unix,posixpaths," \
                     "serverino,mapposix,acl,rsize=1048576,wsize=65536,actimeo=1)"


OSX_MOUNT_OUTPUT = "/dev/disk1s1 on / (apfs, local, journaled)\n" \
                   "devfs on /dev (devfs, local, nobrowse)\n" \
                   "/dev/disk1s4 on /private/var/vm (apfs, local, noexec, journaled, noatime, nobrowse)\n" \
                   "map -hosts on /net (autofs, nosuid, automounted, nobrowse)\n" \
                   "map auto_home on /home (autofs, automounted, nobrowse)\n" \
                   "map -static on /nfs/test_data (autofs, automounted, nobrowse)\n" \
                   "ftp.nervana.sclab.intel.com:/home/nervana/fileshare/data on /nfs/test_data (nfs, nodev, noexec," \
                   " nosuid, read-only, automounted, nobrowse)\n" \
                   f"//username@{MOUNT_IP}/input on /Users/tester/username/mounted_dir " \
                   "(smbfs, nodev, nosuid, mounted by tester)\n" \
                   f"//username2@{MOUNT_IP}/input on /Users/tester/username2/mounted_dir " \
                   "(smbfs, nodev, nosuid, mounted by tester)\n"


def test_get_mount_command_linux(mocker):
    # os library doesn't have getuid function on Windows
    if platform.system() != 'Windows':
        mocker.patch("os.getuid", return_value="10001")

        mount = get_mount_command_linux(TEST_USR, TEST_PSW, TEST_ADR)

        assert mount == CORRECT_LINUX_MOUNT
    else:
        assert True


def test_get_mount_command_windows(mocker):
    mount = get_mount_command_windows(TEST_USR, TEST_PSW, TEST_ADR)

    assert mount == CORRECT_WINDOWS_MOUNT


def test_get_mount_command_osx(mocker):
    mount = get_mount_command_osx(TEST_USR, TEST_PSW, TEST_ADR)

    assert mount == CORRECT_OSX_MOUNT


def test_get_unmount_command_linux(mocker):
    # os library doesn't have getuid function on Windows
    unmount = get_unmount_command_linux()

    assert unmount == CORRECT_LINUX_UNMOUNT


def test_get_unmount_command_windows(mocker):
    unmount = get_unmount_command_windows()

    assert unmount == CORRECT_WINDOWS_UNMOUNT


def test_get_unmount_command_osx(mocker):
    unmount = get_unmount_command_osx()

    assert unmount == CORRECT_OSX_UNMOUNT


def test_mount(mocker):
    host_system = platform.system()

    mocker.patch("commands.mount.is_current_user_administrator", return_value=False)
    gcu_mock = mocker.patch("commands.mount.get_current_user", return_value=TEST_USR)
    gus_mock = mocker.patch("commands.mount.get_users_samba_password", return_value=TEST_PSW)
    cmp_mock = mocker.patch("commands.mount.get_kubectl_host", return_value=TEST_ADR)

    runner = CliRunner()
    # os library doesn't have getuid function on Windows
    if host_system != 'Windows':
        os_getuid_mock = mocker.patch("os.getuid", return_value="10001")

        mocker.patch("platform.system", return_value="Linux")

        result = runner.invoke(mount)

        assert CORRECT_LINUX_MOUNT in result.output
        assert CORRECT_LINUX_UNMOUNT in result.output
        assert Texts.UNMOUNT_OPTIONS_MSG in result.output
        assert os_getuid_mock.call_count == 1

    mocker.patch("platform.system", return_value="Windows")

    result = runner.invoke(mount)

    assert CORRECT_WINDOWS_MOUNT in result.output
    assert CORRECT_WINDOWS_UNMOUNT in result.output
    assert Texts.UNMOUNT_OPTIONS_MSG not in result.output

    mocker.patch("platform.system", return_value="Darwin")

    result = runner.invoke(mount)

    assert CORRECT_OSX_MOUNT in result.output
    assert CORRECT_OSX_UNMOUNT in result.output
    assert Texts.UNMOUNT_OPTIONS_OSX_MSG in result.output

    if host_system != 'Windows':
        call_number = 3
    else:
        call_number = 2

    assert gcu_mock.call_count == call_number
    assert gus_mock.call_count == call_number
    assert cmp_mock.call_count == call_number


def test_get_mounts_windows(mocker, capsys):
    esc_mock = mocker.patch("commands.mount.execute_system_command")
    esc_mock.return_value = WIN_NET_USE_OUTPUT, 0, WIN_NET_USE_OUTPUT
    gkh_mock = mocker.patch("commands.mount.get_kubectl_host")
    gkh_mock.return_value = MOUNT_IP

    get_mounts_windows()
    out, err = capsys.readouterr()

    split_output = out.split("\n")
    assert len(split_output) == 7
    assert f"\\\\{MOUNT_IP}\input" in split_output[2]
    assert "S:" in split_output[2]
    assert "Z:" in split_output[3]
    assert "Microsoft Windows Network" in split_output[4]
    assert f"\\\\{MOUNT_IP}\output" in split_output[5]


def test_get_mounts_linux_non_admin(mocker, capsys):
    esc_mock = mocker.patch("commands.mount.execute_system_command")
    esc_mock.return_value = LINUX_MOUNT_OUTPUT, 0, LINUX_MOUNT_OUTPUT
    gkh_mock = mocker.patch("commands.mount.get_kubectl_host")
    gkh_mock.return_value = MOUNT_IP

    get_mounts_linux_osx(username="username", is_admin=False)
    out, err = capsys.readouterr()

    split_output = out.split("\n")
    assert len(split_output) == 4
    assert f"//{MOUNT_IP}/input" in split_output[2]
    assert "username" in split_output[2]
    assert "/home/username/input" in split_output[2]


def test_get_mounts_linux_admin(mocker, capsys):
    esc_mock = mocker.patch("commands.mount.execute_system_command")
    esc_mock.return_value = LINUX_MOUNT_OUTPUT, 0, LINUX_MOUNT_OUTPUT
    gkh_mock = mocker.patch("commands.mount.get_kubectl_host")
    gkh_mock.return_value = MOUNT_IP

    get_mounts_linux_osx(username="username", is_admin=True)
    out, err = capsys.readouterr()

    split_output = out.split("\n")
    assert len(split_output) == 5
    assert f"//{MOUNT_IP}/input" in split_output[2]
    assert "username" in split_output[2]
    assert "/home/username/input" in split_output[2]
    assert "username2" in split_output[3]


def test_get_mounts_osx_non_admin(mocker, capsys):
    esc_mock = mocker.patch("commands.mount.execute_system_command")
    esc_mock.return_value = OSX_MOUNT_OUTPUT, 0, OSX_MOUNT_OUTPUT
    gkh_mock = mocker.patch("commands.mount.get_kubectl_host")
    gkh_mock.return_value = MOUNT_IP

    get_mounts_linux_osx(username="username", is_admin=False, osx=True)
    out, err = capsys.readouterr()

    split_output = out.split("\n")
    assert len(split_output) == 4
    assert f"{MOUNT_IP}/input" in split_output[2]
    assert "username" in split_output[2]
    assert "/Users/tester/username/mounted_dir" in split_output[2]


def test_get_mounts_osx_admin(mocker, capsys):
    esc_mock = mocker.patch("commands.mount.execute_system_command")
    esc_mock.return_value = OSX_MOUNT_OUTPUT, 0, OSX_MOUNT_OUTPUT
    gkh_mock = mocker.patch("commands.mount.get_kubectl_host")
    gkh_mock.return_value = MOUNT_IP

    get_mounts_linux_osx(username="username", is_admin=True, osx=True)
    out, err = capsys.readouterr()

    split_output = out.split("\n")
    assert len(split_output) == 5
    assert f"{MOUNT_IP}/input" in split_output[2]
    assert "username" in split_output[2]
    assert "/Users/tester/username/mounted_dir" in split_output[2]
    assert "username2" in split_output[3]
    assert "/Users/tester/username2/mounted_dir" in split_output[3]
