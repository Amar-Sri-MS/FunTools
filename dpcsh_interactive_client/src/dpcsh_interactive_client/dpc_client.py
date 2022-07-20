#!/usr/bin/env python3

import json, time, re
import socket, fcntl, errno
import os, sys


class DpcClient(object):
    def __init__(
        self, target_ip, target_port, verbose=False, throw_exception_instead=False
    ):
        """
        Parameters
        ----------
        target_ip: str
            ip
        target_port: int
            port
        verbose: bool
            default False
        throw_exception_instead: bool
            throw exception instead of sys.exit(1), default False

        """
        self.target_ip = target_ip
        self.target_port = target_port
        self.sock = None
        self.verbose = verbose
        self.throw_exception_instead = throw_exception_instead
        self.connect(ensure_connect=True)

    def sendall(self, data):
        while data:
            try:
                sent = self.sock.send(data)
                data = data[sent:]
            except socket.error as e:
                err = e.args[0]
                if err == errno.EAGAIN or err == errno.EWOULDBLOCK:
                    continue

    def _read(self):
        """
        Raises
        ------
        ValueError: exception
            exception raised when self.throw_exception_instead is True
        """
        chunk = 4096
        output = []

        def _check_cr(output):
            if len(output) == 0:
                return False
            return output[-1][-1] == 10  # check `\n', unicode 10 is '\n'

        while not _check_cr(output):
            try:
                buffer = self.sock.recv(chunk)
            except socket.error as e:
                err = e.args[0]
                if err == errno.EAGAIN or err == errno.EWOULDBLOCK:
                    continue
                else:
                    # a "real" error occurred
                    print(e)
                    if self.throw_exception_instead:
                        raise ValueError(
                            "read from {}:{} failed".format(
                                self.target_ip, self.target_port
                            )
                        )
                    else:
                        sys.exit(1)
            else:
                output.append(buffer)

        output[-1] = output[-1].rstrip()  # remove '\n'
        output = [o.decode("utf-8") for o in output]  # byte to string
        output = "".join(output)  # list to string

        return output

    def connect(self, ensure_connect=False):
        if not self.sock:
            self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.sock.connect((self.target_ip, self.target_port))
            fcntl.fcntl(self.sock, fcntl.F_SETFL, os.O_NONBLOCK)
            if ensure_connect:
                self.ensure_connect()

    def read(self):
        json = self._read()
        while (
            (not json)
            or (json.count("{") != json.count("}"))
            or (json.count("[") != json.count("]"))
        ):
            json += self._read()
        return json

    def disconnect(self):
        if self.sock:
            self.sock.close()
        self.sock = None
        return True

    """
    def command(self, command, legacy=False):
        result = None
        output = ""
        try:
            command = "{}\n".format(command)
            if legacy:
                command = "#!sh {}".format(command)
            if self.verbose:
                print("DPCSH Send:" + command + "\n")

            self.sendall(command)
            output = self._read()
            if output:
                actual_output = self._parse_actual_output(output=output)
                try:
                    json_output = json.loads(actual_output.strip())
                except:
                    print("Unable to parse JSON data")
                    json_output = output
                result = json_output
        except socket.error, msg:
            print msg
        except Exception as ex:
            print (str(ex))
            print ("result from read:" + str(output))
        if self.verbose:
            self._print_result(result=output)
        return result
    """

    def _parse_actual_output(self, output):
        actual_output = output
        if re.search(r".*arguments.*", output, re.MULTILINE):
            actual_output = re.sub(r".*arguments.*", "", output, re.MULTILINE)
        return actual_output

    def _print_result(self, result):
        print("Raw DPCSH Result")
        print(result)

    def execute(self, verb, arg_list=None, tid=0):
        jdict = None
        result = None
        output = ""
        try:
            self.connect(ensure_connect=False)
            if arg_list:
                if type(arg_list) is not list:
                    jdict = {"verb": verb, "arguments": [arg_list], "tid": tid}
                elif type(arg_list) is list:
                    jdict = {"verb": verb, "arguments": arg_list, "tid": tid}
            else:
                jdict = {"verb": verb, "arguments": [], "tid": tid}

            command = "{}\n".format(json.dumps(jdict)).encode("utf-8")

            self.sendall(command)
            output = self.read()
            if output:
                # actual_output = self._parse_actual_output(output=output)
                try:
                    # json_output = json.loads(actual_output.strip())
                    json_output = json.loads(output)
                except:
                    if self.verbose:
                        print("Unable to parse JSON data")
                    json_output = output
                if "result" in json_output:
                    result = json_output["result"]
                else:
                    result = json_output
        except socket.error as e:
            print(e)
        except Exception as ex:
            print(str(ex))
            print("result from read:" + str(output))
        if self.verbose:
            self._print_result(result=output)
        return result

    def ensure_connect(self):
        """
        Raises
        ------
        ValueError: exception
            exception raised when self.throw_exception_instead is True
        """
        result = self.execute(verb="echo", arg_list=["hello"])
        if result != "hello":
            print(
                "Connection to DPC server via tcp_proxy at %s:%s failed. "
                % (self.target_ip, self.target_port)
            )
            if self.throw_exception_instead:
                raise ValueError(
                    "connection to {}:{} failed".format(
                        self.target_ip, self.target_port
                    )
                )
            else:
                sys.exit(1)
        else:
            print(
                "Connected to DPC server via tcp_proxy at %s:%s."
                % (self.target_ip, self.target_port)
            )
            # self._set_syslog_level(level=3)

    def _set_syslog_level(self, level):
        try:
            result = self.execute(verb="poke", arg_list=["params/syslog/level", level])
            if result:
                print("Syslog level set to %d" % level)
            else:
                print("Unable to set syslog level")
        except Exception as ex:
            print("ERROR: %s" % str(ex))
