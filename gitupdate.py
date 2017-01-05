#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# Git update main program
# Executed every 5 minutes with cron


import os
from glob import glob
from configparser import ConfigParser

# import config


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
        return True

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
        if repo and repo not in self._repos.keys():
            raise ValueError('Unable to find repository {}.'.format(repo))

        if repo:
            self.repositories[repo].update()
        else:
            for n, r in self.repositories.items():
                print('Updating {}'.format(n))
                r.update()

    @property
    def repositories(self):
        return self._repos


if __name__ == '__main__':
    import argparse

    COMMANDS = ('list', 'update', 'remote')
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
