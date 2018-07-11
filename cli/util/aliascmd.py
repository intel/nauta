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

import click


class AliasCmd(click.Command):
    def __init__(self, *args, **kwargs):
        self._alias = kwargs.pop('alias', '')
        super(AliasCmd, self).__init__(*args, **kwargs)

    def alias(self):
        return self._alias


class AliasGroup(click.Group):
    def __init__(self, *args, **kwargs):
        self._alias = kwargs.pop('alias', '')
        super(AliasGroup, self).__init__(*args, **kwargs)

    def alias(self):
        return self._alias

    def get_command(self, ctx, cmd_name):
        rv = click.Group.get_command(self, ctx, cmd_name)
        if rv is not None:
            return rv
        matches = [x for x in self.list_commands(ctx)
                   if hasattr(click.Group.get_command(self, ctx, x), 'alias')
                   and click.Group.get_command(self, ctx, x).alias() == cmd_name]
        if not matches:
            return None

        return click.Group.get_command(self, ctx, matches[0])

    def format_commands(self, ctx, formatter):
        helper = []
        for cmd in self.list_commands(ctx):
            if cmd is None:
                continue
            c = self.get_command(ctx, cmd)
            alias = c.alias() if hasattr(c, 'alias') else ''
            cmd_name = '{0}, {1}'.format(cmd, alias)
            cmd_help = c.short_help or ''
            helper.append((cmd_name, cmd_help))
        if helper:
            with formatter.section('Commands'):
                formatter.write_dl(helper)

    def collect_usage_pieces(self, ctx):
        # Skip first element of usage pieces of this command. This will be "[OPTIONS]".
        rv = super(AliasGroup, self).collect_usage_pieces(ctx)[1:]
        return rv
