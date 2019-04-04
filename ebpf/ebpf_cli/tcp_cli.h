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

#define NBUF_SZ 512

class tcp_cli {
    private:
        int sock;
	char* net_buf;
    public:
        tcp_cli();
	~tcp_cli();
        bool conn(const std::string& host, const int& port);

        bool send_data(const std::string& data);
        bool send_data(uint8_t* arr, size_t len);

        std::string receive();
};
