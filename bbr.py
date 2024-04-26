#!/usr/bin/env python
# -*- coding: utf-8 -*-
from subprocess import check_call, CalledProcessError
from threading import Thread
import arg_parser
import context
from helpers import kernel_ctl
import sys
from concurrent.futures import ThreadPoolExecutor
import concurrent


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
    with ThreadPoolExecutor(max_workers=len(commands)) as executor:
        # 将命令映射到线程池上的工作者
        future_to_cmd = {executor.submit(run_command, cmd): cmd for cmd in commands}

        # 获取结果
        for future in concurrent.futures.as_completed(future_to_cmd):
            cmd = future_to_cmd[future]
            try:
                result = future.result()
                print(result)
            except Exception as exc:
                print('Command generated an exception: {} - {}'.format(cmd, exc))

    print("All commands completed.")


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
