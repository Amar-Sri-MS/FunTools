/*
 * Test client for dbgsh_agent. Steps to build and use
 * gcc dbgsh_client.c
 * ./a.out
 * 
 * Copyright © 2023 Microsoft. All rights reserved
 */
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <sys/types.h>
#include <sys/socket.h>
#include <netinet/in.h>
#include <arpa/inet.h>
#include <unistd.h>

#define PORT 65432
#define HOST "127.0.0.1"
#define AGENT_REQ_CSR_READ 1
#define AGENT_REQ_CSR_WRITE 2

//F1D1 ZIP Scratchpad Register
#define CSR_ADDRESS 0x58e9130
#define TEST_VALUE 0xCCDDEE
#define PROTOCOL_VERSION 1
#define REQUEST_ID 1

struct dbgsh_agent_req {
    uint32_t version;
    uint32_t id;
    uint32_t op;
    uint32_t status;
    uint64_t addr;
    uint64_t val;
};

struct dbgsh_agent_req pack_data(uint32_t protocol_version, uint32_t request_id, uint32_t message_opcode, uint32_t status, uint64_t address, uint64_t value) {
    struct dbgsh_agent_req data;
    data.version = protocol_version;
    data.id = request_id;
    data.op = message_opcode;
    data.status = status;
    data.addr = address;
    data.val = value;
    return data;
}

ssize_t recv_exact(int sock, char *buffer, size_t num_bytes) {
    size_t bytes_received = 0;
    while (bytes_received < num_bytes) {
        ssize_t ret = recv(sock, buffer + bytes_received, num_bytes - bytes_received, 0);
        if (ret <= 0) return ret;
        bytes_received += ret;
    }
    return bytes_received;
}

void tcp_client() {
    int s = socket(AF_INET, SOCK_STREAM, 0);
    struct sockaddr_in server_addr;
    server_addr.sin_family = AF_INET;
    server_addr.sin_port = htons(PORT);
    inet_pton(AF_INET, HOST, &(server_addr.sin_addr));

    connect(s, (struct sockaddr*)&server_addr, sizeof(server_addr));

    struct dbgsh_agent_req msg = pack_data(PROTOCOL_VERSION, REQUEST_ID, AGENT_REQ_CSR_READ, 0, CSR_ADDRESS, 0x0);
    send(s, &msg, sizeof(msg), 0);
    printf("Waiting for response\n");

    recv_exact(s, (char*)&msg, sizeof(msg));
    printf("Received from server: version: %u, id: %u, op: %u, status: %u, address: %#lx, val: %#lx\n", msg.version, msg.id, msg.op, msg.status, msg.addr, msg.val);

    msg = pack_data(PROTOCOL_VERSION, REQUEST_ID, AGENT_REQ_CSR_WRITE, 0, CSR_ADDRESS, TEST_VALUE);
    printf("Sending poke command\n");
    send(s, &msg, sizeof(msg), 0);

    printf("Waiting for response\n");
    recv_exact(s, (char*)&msg, sizeof(msg));

    if (msg.status == 0) {
        printf("Poke successful\n");
        printf("Peeking again\n");
        msg = pack_data(PROTOCOL_VERSION, REQUEST_ID, AGENT_REQ_CSR_READ, 0, CSR_ADDRESS, 0x0);
        send(s, &msg, sizeof(msg), 0);
        recv_exact(s, (char*)&msg, sizeof(msg));
        printf("Received from server: version: %u, id: %u, op: %u, status: %u, address: %#lx, val: %#lx\n", msg.version, msg.id, msg.op, msg.status, msg.addr, msg.val);
        if(msg.val == TEST_VALUE) {
            printf("Poke successful\n");
        }
    } else {
        printf("Poke failed\n");
    }

    close(s);
}

int main() {
    tcp_client();
    return 0;
}
