#!/usr/bin/env python3
import argparse
import socket
import re
import time
from argo_probe_ams_publisher.NagiosResponse import NagiosResponse

maxcmdlength = 128
timeout = 10


def parse_result(query):
    w = None
    try:
        w, r = query.split('+')

        w = w.split(':')[1]
        r = int(r.split(':')[1])

    except (ValueError, KeyError):
        return w, 'error'

    return w, r


def extract_intervals(queries):
    intervals = list()

    for q in queries:
        get = q.split('+')[1]
        i = re.search('[0-9]+$', get).group(0)
        intervals.append(int(i))

    return intervals


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        '-s', dest='socket', required=True, type=str,
        help='AMS inspection socket'
    )
    parser.add_argument(
        '-q', dest='query', action='append', required=True, type=str,
        help='Query'
    )
    parser.add_argument(
        '-c', dest='threshold', action='append', required=True, type=int,
        help='Threshold'
    )
    parser.add_argument(
        '-t', dest='timeout', required=False, type=int, help='Timeout'
    )
    arguments = parser.parse_args()

    nr = NagiosResponse()

    if len(arguments.threshold) != len(arguments.query):
        nr.setCode(2)
        nr.writeCriticalMessage('Wrong arguments')
        print(nr.getMsg())
        raise SystemExit(nr.getCode())

    if arguments.timeout:
        timeo = arguments.timeout

    else:
        timeo = timeout

    sock = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
    try:
        sock.setblocking(False)
        sock.settimeout(timeo)

        sock.connect(arguments.socket)
        sock.send(' '.join(arguments.query), maxcmdlength)
        data = sock.recv(maxcmdlength)

        starttime = None
        lr = list()
        for r in data.split():
            if r.startswith('t:'):
                starttime = int(r.split(':')[1])
                continue
            lr.append(parse_result(r))

        intervals = extract_intervals(arguments.query)
        now = int(time.time())
        if now - starttime < 60 * max(intervals):
            nr.setCode(1)
            nr.writeWarningMessage(
                f'No results yet, ams-publisher is not running for '
                f'{max(intervals)} minutes'
            )
            print(nr.getMsg())
            raise SystemExit(nr.getCode())

        error = False
        for e in lr:
            if e[1] == 'error':
                nr.setCode(2)
                nr.writeCriticalMessage(f'Worker {e[0]} {e[1]}')
                error = True
        if error:
            print(nr.getMsg())
            raise SystemExit(nr.getCode())

        error = False
        nr.setCode(0)
        i = 0
        while i < len(lr):
            e = lr[i]
            if e[1] < arguments.threshold[i]:
                nr.setCode(2)
                nr.writeCriticalMessage(
                    f'Worker {e[0]} published {e[1]} (threshold '
                    f'{arguments.threshold[i]} in {intervals[i]} minutes)'
                )
                error = True

            i += 1

        if error:
            print(nr.getMsg())
            raise SystemExit(nr.getCode())
        else:
            i = 0
            nr.setCode(0)
            while i < len(lr):
                e = lr[i]
                nr.writeOkMessage(
                    f'Worker {e[0]} published {e[1]} (threshold '
                    f'{arguments.threshold[i]} in {intervals[i]} minutes)'
                )
                i += 1

            print(nr.getMsg())
            raise SystemExit(nr.getCode())

    except socket.timeout:
        nr.setCode(2)
        nr.writeCriticalMessage(f'Socket response timeout after {timeo} s')
        print(nr.getMsg())
        raise SystemExit(nr.getCode())

    except socket.error as e:
        nr.setCode(2)
        nr.writeCriticalMessage(f'Socket error: {str(e)}')
        print(nr.getMsg())
        raise SystemExit(nr.getCode())

    finally:
        sock.close()


if __name__ == "__main__":
    main()
