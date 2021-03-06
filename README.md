# Gmail Export Command Line Tool

Exporting attachments including png, jpg, gif, pdf etc. with simple command line from your gmail account.  

### Requirements

- python 2.7
- [pygmail author by @snyderp](https://github.com/snyderp/pygmail)

### Options

| Parameter | Long Parameter | Description                                                        |
|-----------|----------------|--------------------------------------------------------------------|
| -e        | --email        | gmail address                                                      |
| -p        | --password     | password for gmail                                                 |
| -d        | --dest         | The path where attachments should be downloaded (default to ``.``).|
| -l        | --limit        | The total number of messages that should be downloaded from GMail. Default is 0, or all. |
| -s        | --simultaneous | The maximum number of messages that should be downloaded from GMail at a time (defaults to 10).|

### Run

```shell
$ pip install --no-cache-dir -r requirements.txt
$ python app.py -e $GMAIL_ACCOUNT -p $GMAIL_PASSWORD
```

### Thanks to

- @snyderp