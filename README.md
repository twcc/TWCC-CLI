###### tags: `twcc`, `twccli`

[![CircleCI](https://circleci.com/gh/TW-NCHC/TWCC-CLI/tree/v0.5.svg?style=shield)](https://circleci.com/gh/TW-NCHC/TWCC-CLI/tree/v0.5)


# TWCC-CLI Project

The TWCC Command Line Interface (CLI) is an environment to create and manage your TWCC services. The current version of the TWCC CLI is **v0.5**. (New version coming soon! Please checkout **New Features** below.)

**NOTICE**
Remeber to set locale in environment
```
export LANG=C.UTF-8
export LC_ALL=C.UTF-8
export PYTHONIOENCODING=UTF-8
```

## INDEX: 
1. [TWCC-CLI α for v0.5](https://github.com/TW-NCHC/TWCC-CLI/tree/v0.5) | [@PYPI](https://pypi.org/project/TWCC-CLI/)
1. Release Notes

### v0.5.6 Release Note
![img](https://media.giphy.com/media/xUA7b7yLPq3IPOLnk4/giphy.gif)

**new features**
- You can create additional data volume in `ssd` and `ssd-encrypt` type.

**fix bug**
- upload file source path with slash is not work.
- adding error condition in `rm ccs -s` while entering resource name, and adding `-s` parameter in `ls ccs`.
- fix naming standard to 6-16 in length.
- support customized clone image in CCS.

### v0.5.5 Release Note
![img](https://media.giphy.com/media/xThuWmOkO0SvRprLXy/giphy.gif)


**new features**
- snapshot delete functions, `twccli rm vsc -snap -snap-id $SNAPTSHOT_ID`

**fix bug**
- delete bucket and file operation
- upload and download dir to bucket
- remove flag 'noforce' in `twccli rm`
- update listing all snapshots for Project Owner
- `rm vcs` with `-s` flag

### v0.5.4 Release Note
![img](https://media.giphy.com/media/MtIPR6C5okdt6/giphy.gif)


**new features**
- provides encoding setting, `twccli config init --set-bashrc`

**fix bug**
- no data while listing VCS 
- can't delete bucket with data recursively
- can't download hierarchy directory to local site 
- modify parameter and description in command "CP"

### v0.5.3 Release Note

![img](https://media.giphy.com/media/xHMIDAy1qkzNS/giphy.gif)

**new features**
- We add encoding environ setting
- add keypair write and del file
- add private ip and network info while ls vcs

**fix**
- fix create keypair's bug
- fix error in `MANIFEST.in`, remove vcs cos, list vcs, --help description of cos


### v0.5.2 Release Note
**New and structured CLI commands!**

for Mar. 20th ,2020 (v0.5.2)
  - Now you can use structured commands`config`, `mk`, `ls`, `rm`, `cp`, and `net` to customize and manage your TWCC Compute and Storage services, including VCS, CCS, and COS.
  - In addition to CCS and COS, now you can use TWCC CLI to manage your VCS resources, including VCS instances, security groups, snapshots, as well as keypairs.
  - Use commands`-table` or `-json show` to clearly diaplay your resource information in a table view or in JSON.


## Contact us
If you have any questions, please email us at: 
- iservice@narlabs.org.tw for account support
- isupport@narlabs.org.tw for technical support
