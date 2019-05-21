# MIPS Dequeuer

This folder contains the JAR file for the MIPS dequeuer,
which is used to convert pdtrace raw daa into trace messages.

It also contains a Fungible shell script to launch the dequeuer.
The dequeuer has odd expectations about stdin, and the script
attempts to fulfil those expectations when run as a daemon
(without a tty stdin).

Note that this contains MIPS proprietary code, so beware before
shipping anything in this directory.