#include "tcp_cli.h"
#include <iostream>

tcp_cli::tcp_cli(void):sock(-1) {}

bool tcp_cli::conn(const std::string& host, const int& port) {
    struct sockaddr_in server;
    if (sock == -1) {
         sock = socket(AF_INET, SOCK_STREAM, 0);
	 if (sock == -1) {
            perror("socket create");
	    return false;
	 }
    }
    std::cout << "Socket created" << std::endl;
    if (inet_addr(host.c_str()) == -1) {
        struct hostent* he;
	struct in_addr** addr_list;
	if ((he = gethostbyname(host.c_str())) == nullptr) {
            perror("gethostbyname");
	    return false;
	}
	addr_list = (struct in_addr** )he->h_addr_list;
	for (auto i = 0; addr_list[i] != nullptr; i ++) {
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

bool tcp_cli::send_data(const std::string& data) {
    if(send(sock, data.c_str(), strlen(data.c_str()), 0) < 0) {
        perror("Send failed");
	return false;
    }
    return true;
}
std::string tcp_cli::receive(const int& sz = 1024) {
    char buffer[sz];
    if(recv(sock, buffer, sizeof(buffer), 0) < 0) {
        perror("Recv failed");
    } 
    return std::string{buffer};
}
