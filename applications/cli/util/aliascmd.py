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

    def get_help_option(self, ctx):
        help_options = self.get_help_option_names(ctx)
        if not help_options or not self.add_help_option:
            return

        def show_help(ctx, param, value):
            if value and not ctx.resilient_parsing:
                click.echo(ctx.get_help(), color=ctx.color)
                ctx.exit()

        return click.Option(help_options, is_flag=True, is_eager=True, expose_value=False, callback=show_help,
                            help='Displays help messaging information.')
