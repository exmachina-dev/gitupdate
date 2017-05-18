gitupdate
=========

Gitupdate is a tool that allow you to propagate changes on a git server to multiple remotes

# Installation & configuration

Clone this repository and add your configuration files in the `conf/` directory

The following syntax apply:
```conf
[PATH_TO_REPO]
remote.REMOTE_NAME = git@exmaple.com:repository.git
```

In order to update configuration automatically, add in your post-receive hook
```sh
git update-server-info

GITUPDATE_DIR='/home/git/gitupdate/'

GIT_WORK_TREE=$GITUPDATE_DIR git checkout -f

cd $GITUPDATE_DIR
python3 $(GITUPDATE_DIR)gitupdate.py update_remotes
```

To update repository you can either run a cron task with the following command
```cron
0       */1     *       *       * python3 /home/git/gitupdate/gitupdate.py update
```

Or add in each repository post-receive hook
```sh
python3 /home/git/gitupdate/gitupdate.py update --repository=PATH_TO_REPO
```

NOTE: `PATH_TO_REPO` is the path from your git repositories root.

# License

This library is licensed under MIT. For more details, see the [License file](LICENSE).

# Credits

Original work by [Benoit Rapidel](mailto:benoit.rapidel+devs AT exmachina.fr)

The original source code can be found at [ExMachina repository](https://github.com/exmachina-dev/gitupdate)
