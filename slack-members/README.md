# Slack Members
Retrieves all members from a slack channel and returns it in CSV format.

## Context
I wanted to segment mailing list based on Slack Channel members. I did not find a simple solution to fetch members list from a Slack Channel or a Group. So I wrote a small script called `membersof.rb` what extract a csv formatted list.

## Requironemnts
### Ruby with Standard Library
You can use several tools to install Ruby. Check it out at https://www.ruby-lang.org/en/documentation/installation/

### Slack Tocken
You can generate or find your personal Slack token here: https://api.slack.com/custom-integrations/legacy-tokens

### Slack Channel or Group ID
You can either call [channels.list](https://api.slack.com/methods/channels.list) to get the list of all channels and to convert the channel name to its ID.
Or.
On Slack Web interface the link to Channels or Groups contains the ID

## Run
```
$ ./membersof.rb --help
This script retrieves all members from a slack channel
Usage: ./membersof.rb [options]
    -t, --token Slack tocken         How to get: https://api.slack.com/custom-integrations/legacy-tokens
    -g, --group Group ID             How to get: https://api.slack.com/methods/groups.list
    -c, --channel Channel ID         How to get: https://api.slack.com/methods/channels.list
```

Example:
Please be aware this methode can take 1-2 sec for each member. Be patient!!
```
$ ./membersof.rb -t xoxp-123456789A-BCDEF01234-56789ABCDE-F012345678 -g QWERTYUIO
first_name,last_name,email
John,Doe,john.doe@example.com
Jane,Doe,jane.doe@example.com
```