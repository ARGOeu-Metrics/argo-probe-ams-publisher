# argo-probe-ams-publisher

Probe is inspecting AMS publisher running on Nagios monitoring instances. It's inspecting trends of published messages for each spawned worker and raises alarm if number of published messages of any worker is below expected threshold. It queries local inspection socket that publisher exposes and reports back status with the help of NRPE Nagios system.

## Synopsis

Probe has several arguments:

```
/usr/libexec/argo/probes/ams-publisher/ams-publisher-probe --help
usage: ams-publisher-probe [-h] -s SOCKET -q QUERY -c THRESHOLD [-t TIMEOUT]

optional arguments:
  -h, --help    show this help message and exit
  -s SOCKET     AMS inspection socket
  -q QUERY      Query
  -c THRESHOLD  Threshold
  -t TIMEOUT    Timeout
```

Example of probe execution: 

```
/usr/libexec/argo/probes/ams-publisher/ams-publisher-probe -q 'w:metrics+g:published180' -c 4000 -s /var/run/ams-publisher/sock
OK - Worker metrics published 21400 (threshold 4000 in 180 minutes)
```
