# Data Replication Script

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
`--mail-smtp-server`   | String       | `mail.domain.com`
`--mail-smtp-user`     | String       | `sender@domain.com`
`--mail-smtp-port`     | String       | `465`,`587`
`--mail-smtp-password` | String       | `&7df>":@1#0=-3]df=*&%!`,`abc123`
`--mail-recipient`     | String       | `recipient@domain.com`

- **Then, invoke `replication.py` and grab the popcorn.**

## For scheduled use (systemd-timer):

To be filled.

## For scheduled use (cron):

To be filled.

