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
            yield r

    def update_remotes(self):
        os.chdir(self.path)

        r = sp.run((GIT_COMMAND, 'remote', '-v'),
                   stdout=sp.PIPE, universal_newlines=True)

        if r.returncode != 0:
            raise ValueError('Something bad happened: {}'.format(r.returncode))

        git_remotes = {}

        for remote in r.stdout.split('\n'):
            if len(remote) == 0:
                continue

            r, t = remote.split(" ")
            n, u = r.split('\t')
            if 'push' in t:
                git_remotes[n] = u

        if git_remotes == self.remotes:
            return False

        # Removing remotes erased from config files
        for git_remote, url in self.git_remotes.items():
            if git_remote not in self.remotes.keys():
                print('Removing remote {}:'.format(git_remote), end='')
                if not sp.run((GIT_COMMAND, 'remote', 'remove',
                              git_remote)):
                    print(' Failed.')
                else:
                    print(' Done.')

        # Adding or updating remotes from config files
        for cnf_remote, url in self.remotes.items():
            if cnf_remote in git_remotes.keys():
                if url != git_remotes[cnf_remote]:
                    print('Updating remote {} to {}:'.format(cnf_remote, url),
                           end='')
                    if not sp.run((GIT_COMMAND, 'remote', 'set-url',
                                  cnf_remote, url)):
                        print(' Failed.')
                    else:
                        print(' Done.')
            else:
                print('Adding remote {} at {}:'.format(cnf_remote, url), end='')
                if not sp.run((GIT_COMMAND, 'remote', 'add', cnf_remote, url)):
                    print(' Failed.')
                else:
                    print(' Done.')

        return True

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
                        print('Updating {} remote:'.format(n), end='')
                    else:
                        if res.returncode != 0:
                            print(' Failed:', res.stderr)
                        else:
                            print(' Done.')

    def update_remotes(self, repo=None):
        if repo:
            if repo not in self._repos.keys():
                raise ValueError('Unable to find repository {}.'.format(repo))

            self.repositories[repo].update_remotes()
        else:
            for n, r in self.repositories.items():
                print('Updating {}:'.format(n), end='')

                if r.update_remotes():
                    print('\tDone.')
                else:
                    print(' Nothing to do.')

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
