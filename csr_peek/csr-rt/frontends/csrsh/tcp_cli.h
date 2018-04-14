/*
 *  tcp_cli.h
 *
 *  Created by Hariharan Thantry on 2018-02-28
 *
 *  Copyright © 2018 Fungible Inc. All rights reserved.
 */
#pragma once

#include <string.h>
#include <string>
#include <sys/socket.h>
#include <arpa/inet.h>
#include <netdb.h>

class tcp_cli {
    private:
        int sock;
    public:
        tcp_cli();
        bool conn(const std::string& host, const int& port);
        bool send_data(const std::string& data);
        std::string receive(const int& sz=1024);
};
