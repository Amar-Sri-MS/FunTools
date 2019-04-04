/*
 *  tcp_cli.cpp
 *
 *  Created by Hariharan Thantry on 2018-02-28
 *
 *  Copyright © 2018 Fungible Inc. All rights reserved.
 */
#include <cassert>
#include <cstring>
#include <iostream>

#include "tcp_cli.h"

#ifdef __cplusplus
extern "C" {
#endif
#include <utils/threaded/fun_json.h>
#ifdef __cplusplus
}
#endif

tcp_cli::tcp_cli(void) : sock(-1), net_buf{new char[NBUF_SZ]()} {}

tcp_cli::~tcp_cli(void) {
    delete[] net_buf;
    net_buf = nullptr;
}

bool tcp_cli::conn(const std::string &host, const int &port) {
    struct sockaddr_in server;
    if (sock == -1) {
        sock = socket(AF_INET, SOCK_STREAM, 0);
        if (sock == -1) {
            perror("socket create");
            return false;
        }
    }
    std::cout << "Socket created" << std::endl;
    if (inet_addr(host.c_str()) == (in_addr_t)(-1)) {
        struct hostent *he;
        struct in_addr **addr_list;
        if ((he = gethostbyname(host.c_str())) == nullptr) {
            perror("gethostbyname");
            return false;
        }
        addr_list = (struct in_addr **)he->h_addr_list;
        for (auto i = 0; addr_list[i] != nullptr; i++) {
            server.sin_addr = *addr_list[i];
            break;
        }
    } else {
        server.sin_addr.s_addr = inet_addr(host.c_str());
    }
    std::cout << "Server resolved" << std::endl;
    server.sin_family = AF_INET;
    server.sin_port = htons(port);
    if (connect(sock, (struct sockaddr *)&server, sizeof(server)) < 0) {
        perror("Connect failed");
        return false;
    }
    std::cout << "Connected" << std::endl;
    return true;
}

bool tcp_cli::send_data(uint8_t *byte_arr, size_t len) {
    if (send(sock, byte_arr, len, 0) < 0) {
        perror("Send failed");
        return false;
    }
    return true;
}

bool tcp_cli::send_data(const std::string &data) {
    std::cout << "Sending Data: " << data;

    if (send(sock, data.c_str(), strlen(data.c_str()), 0) < 0) {
        perror("Send failed");
        return false;
    }
    return true;
}

std::string tcp_cli::receive() {
    std::string rsp;
    int rcv_sz;
    while (1) {
        std::memset(net_buf, 0, NBUF_SZ);
        if ((rcv_sz = recv(sock, net_buf, NBUF_SZ, 0)) < 0) {
            if (rsp.empty()) {
                std::cout << "***Rxed Empty***" << std::endl;
                assert(false);
            }
            break;
        } else {
            rsp += net_buf;
        }

        if (rcv_sz < NBUF_SZ) {
            if (net_buf[rcv_sz - 1] != '\n') continue;
            break;
        }
    }
    return rsp;
}
