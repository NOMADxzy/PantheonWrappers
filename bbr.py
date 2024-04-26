#!/usr/bin/env python
# -*- coding: utf-8 -*-
from subprocess import check_call, CalledProcessError
from threading import Thread
import arg_parser
import context
from helpers import kernel_ctl
import sys


def setup_bbr():
    # load tcp_bbr kernel module (only available since Linux Kernel 4.9)
    kernel_ctl.load_kernel_module('tcp_bbr')

    # add bbr to kernel-allowed congestion control list
    kernel_ctl.enable_congestion_control('bbr')

    # check if qdisc is fq
    kernel_ctl.check_qdisc('fq')


def run_command(cmd):
    try:
        check_call(cmd)
        print("Command succeeded:", cmd)
    except CalledProcessError as e:
        print("Command failed with return code", e.returncode, ":", cmd)


def run_cmds_together(commands):
    # 为每个命令创建一个线程
    threads = []
    for cmd in commands:
        thread = Thread(target=run_command, args=(cmd,))
        thread.start()
        threads.append(thread)

    # 等待所有线程完成
    for thread in threads:
        thread.join()


def main():
    flows = 5
    args = arg_parser.receiver_first()

    if args.option == 'deps':
        print 'iperf'
        return

    if args.option == 'setup_after_reboot':
        setup_bbr()
        return

    if args.option == 'receiver':
        commands = []
        port0 = int(args.port)
        for port in range(port0, port0 + flows):
            cmd = ['iperf', '-Z', 'bbr', '-s', '-p', str(port)]
            commands.append(cmd)
        run_cmds_together(commands=commands)
        return

    if args.option == 'sender':
        commands = []
        port0 = int(args.port)
        for port in range(port0, port0 + flows):
            cmd = ['iperf', '-Z', 'bbr', '-c', args.ip, '-p', str(port),
                   '-t', '75']
            commands.append(cmd)

            sys.stderr.write(str(cmd))
        run_cmds_together(commands=commands)
        return


if __name__ == '__main__':
    main()
