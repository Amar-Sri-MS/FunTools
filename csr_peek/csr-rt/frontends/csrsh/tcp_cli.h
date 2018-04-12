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
        std::string receive(const int& sz);	
};
