#!/usr/bin/env python

from os import path
from subprocess import check_call

import arg_parser
import context, socket, subprocess


def try_start_rpc_server(cc_repo):
    rpc_src = '/home/nomad/work/MFGModel/rlServer.py'
    #rpc_src = path.join(cc_repo, 'rlServer.py')
    cmd = ["python", rpc_src]
    proc = subprocess.Popen(cmd)
    print "------rpc_start-------"
    return proc
 


def main():
    flows = "5"
    args = arg_parser.sender_first()

    cc_repo = path.join(context.third_party_dir, 'indigo_a3c_test')
    send_src = path.join(cc_repo, 'a3c', 'run_sender.py')
    recv_src = path.join(cc_repo, 'env', 'run_receiver.py')

    if args.option == 'setup':
        check_call(['sudo pip install tensorflow==1.14.0'], shell=True)
        return

    if args.option == 'sender':
        cmd = ['python', send_src, args.port] + [flows]
	#proc = try_start_rpc_server(cc_repo)
	
        check_call(cmd)
        return

    if args.option == 'receiver':
        cmd = ['python', recv_src, args.ip, args.port] + [flows]
        check_call(cmd)
        return


if __name__ == '__main__':
    main()
