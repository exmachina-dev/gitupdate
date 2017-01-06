#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# Git update main program
# Executed every 5 minutes with cron


import os
import subprocess as sp
from glob import glob
from configparser import ConfigParser

# import config

GIT_COMMAND = '/usr/bin/git'
GIT_ROOT = '/home/git/repositories'


class Repository(object):
    def __init__(self, name, r=None):
        self.name = name
        self.remotes = {}
        self.conf = {}
        self.refresh_interval = 120

        if r:
            for k in r.keys():
                if k.startswith('conf.'):
                    self.conf[k[5:]] = r[k]
                elif k.startswith('remote.'):
                    self.remotes[k[7:]] = r[k]
                else:
                    raise ValueError('Invalid key found: {}'.format(k))

    def update(self):
        os.chdir(self.path)

        for remote, url in self.remotes.items():
            yield remote, url
            r = sp.run((GIT_COMMAND, 'push', '--mirror', remote),
                       stdout=sp.PIPE, stderr=sp.PIPE)
            yield r.returncode

    @property
    def path(self):
        return os.path.abspath(GIT_ROOT + '/' + self.name + '.git')

    def __repr__(self):
        return '{}: {}'.format(self.name, ' '.join(self.remotes.values()))


class Gitupdate(object):
    def __init__(self, conf_dir):
        self._conf = ConfigParser()
        self._conf_dir = os.path.abspath(conf_dir + '/')

        self._repos = {}

        if not os.path.isdir(self._conf_dir):
            raise SystemError('Incorrect path for config files')

        self.find_repositories()

    def find_repositories(self):
        self.load_files()

        for repo_conf in self._conf.sections():
            self._repos[repo_conf] = Repository(repo_conf,
                                                self._conf[repo_conf])

    def load_files(self):
        files = glob('{}/*.conf'.format(self._conf_dir))

        self._conf.read(files)

    def update(self, repo=None):
        if repo:
            if repo not in self._repos.keys():
                raise ValueError('Unable to find repository {}.'.format(repo))

            self.repositories[repo].update()
        else:
            for n, r in self.repositories.items():
                print('Updating {}'.format(n))

                for res in r.update():
                    if isinstance(res, tuple):
                        n, u = res
                        print('Updating {} remote:'.format(n),)
                    else:
                        print(' {}'.format(res))

    def update_remotes(self, repo=None):
        if repo:
            if repo not in self._repos.keys():
                raise ValueError('Unable to find repository {}.'.format(repo))

            self.repositories[repo].update_remotes()
        else:
            for n, r in self.repositories.items():
                print('Updating {}'.format(n))

                for res in r.update_remotes():
                    print(res)

    @property
    def repositories(self):
        return self._repos


if __name__ == '__main__':
    import argparse

    COMMANDS = ('list', 'update', 'update_remotes')
    parser = argparse.ArgumentParser(description="Update git repositories")
    parser.add_argument('command', type=str, choices=COMMANDS,
                        help="Command to execute")
    parser.add_argument('--repository', '-r', type=str, required=False,
                        help="Repository")

    args = parser.parse_args()

    gu = Gitupdate('./conf')

    if args.command == 'list':
        print('Available repositories:')
        print(' '.join(gu.repositories))
    elif args.command == 'update':
        gu.update(args.repository)
    elif args.command == 'update_remotes':
        gu.update_remotes(args.repository)
