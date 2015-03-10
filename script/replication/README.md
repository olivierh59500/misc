# Directory Replication Script

This particular script, which behaves as a rsync wrapper, was developed with the personal intention of replicating specific directories over to remote servers on a daily basis, while maintaining [rsync exclude configuration files](http://www.howtogeek.com/168009/how-to-exclude-files-from-rsync/) and logs within the directory said script resides in. It also features the convenient ability to send email notifications indicating the status of such a task.

This was created out of mere desperation to modernize this very process that was once handled by a bash script, which contained aesthetically unpleasing, redundant, static code that I feel should cease to exist in my environment. Due to this work and the existence of Python, I am no longer clutching my pearls.

## Getting Started:

- **From within a shell, use `wget` or `curl` to download `replication.py`:**
```
wget https://raw.githubusercontent.com/misterpeguero/misc/master/script/replication/replication.py
```
```
curl -O https://raw.githubusercontent.com/misterpeguero/misc/master/script/replication/replication.py
```

- **Mark `replication.py` as an executable:**
```
chmod +x replication.py
```

- **Prior to invocation, ensure to specify the following parameters:**

Parameter              | Type         | Example Value
---------              | ----         | -------------
`--src-dir`            | List (Array) | `/foo`, `/foo/ping,/foo/pong`
`--dest-dir`           | String       | `/bar`
`--dest-hostname`      | String       | `machine.domain.com`,`10.0.0.1`
`--dest-ssh-user`      | String       | `user`
`--dest-ssh-port`      | String       | `22`
`--mail-smtp-server`   | String       | `smtp.domain.com`
`--mail-smtp-user`     | String       | `sender@domain.com`
`--mail-smtp-port`     | String       | `465`,`587`
`--mail-smtp-password` | String       | `&7df>":@1#0=-3]df=*&%!`,`abc123`
`--mail-recipient`     | String       | `recipient@domain.com`

- **Then, upon invoking `replication.py`, you will begin to notice output similar to the following example:**
```
OK: Created (Required Script Subdirectory) - "/home/misterpeguero/replication_script/exclude"
OK: Created (Required Script Subdirectory) - "/home/misterpeguero/replication_script/log"

---- FOO ----

OK: Found (Directory) - "/foo"
OK: Created (Exclude List) - "/home/misterpeguero/replication_script/exclude/_foo-machine.domain.com.conf"

----

Invoking Command: /usr/bin/rsync -avrtpzP --rsync-path="/usr/bin/sudo /usr/bin/rsync" -e "ssh -p 22" --delete --exclude-from="/home/misterpeguero/replication_script/exclude/_foo-machine.domain.com.conf" "/foo" user@machine.domain.com:"/bar/" --log-file="/home/misterpeguero/replication_script/log/machine.domain.com_2015-01-01_00-00-00.log"

sending incremental file list
foo/file1.txt
            0 100%  1.00MB/s    0:00:00 (xfr#1, to-chk=4/4)
foo/ping/
foo/ping/file1.txt
            0 100%  1.00MB/s    0:00:00 (xfr#1, to-chk=3/4)
foo/pong/
foo/pong/file1.txt
            0 100%  1.00MB/s    0:00:00 (xfr#2, to-chk=2/4)
foo/pong/file2.txt
            0 100%  1.00MB/s    0:00:00 (xfr#3, to-chk=1/4)

sent 0 bytes  received 0 bytes  0 bytes/sec
total size is 0  speedup is 0

----

OK: Invocation attempt was successful.
OK: Notification attempt was successful.

Process finished. (0)
```

- **Once `replication.py` has terminated, an email notification consisting of the following information will be sent to the specified recipient (`recipient@domain.com`):**
```
Subject : Directory Replication [machine.domain.com_2015-01-01_00-00-00] (SUCCESS)
Body    : Process completed successfully.
```

- **And a new log file will be generated at `log/machine.domain.com_2015-01-01_00-00-00.log`.**

## Exclude Lists:

In the previous output example, you may have noticed this particular message:
```
OK: Created (Exclude List) - "/home/misterpeguero/replication_script/exclude/_foo-machine.domain.com.conf"
```
An exclude list configuration file makes use of rsync's `--exclude-from` parameter and is created whenever a source directory is specified. The purpose of this particular file is to exclude specific subdirectories and/or files from replication. In the case of this script, `_foo-machine.domain.com.conf` consists of a naming scheme that indicates its relation to its respective source directory, `/foo`, and the source directory's specified destination hostname, `machine.domain.com`. Underscores represent forward slashes, as well. To provide a simpler understanding of this explanation, here is a breakdown of the syntax in question:

1. `_(SOURCE DIRECTORY PATH)-(DESTINATION HOSTNAME).conf`
2. `_foo-machine.domain.com.conf`
3. **`/foo machine.domain.com`**

To take advantage of exclude list configuration files, the following examples can be specified:
```
ping
ping/file1.txt
pong
pong/file*
*.txt
```

For more information on the syntax of exclude list configuration files, consult [this](http://www.howtogeek.com/168009/how-to-exclude-files-from-rsync/) article from How-To-Geek.

## For Scheduled Use:

This script was developed with the intention of automating a directory replication process and can be used in conjuction with `systemd-timer` and `cron`.
