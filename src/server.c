#include "server.h"
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <pthread.h>
#include <unistd.h>
#include <arpa/inet.h>

static Client clients[MAX_CLIENTS];
static int client_count = 0;
static pthread_mutex_t clients_mutex = PTHREAD_MUTEX_INITIALIZER;
static FILE *log_file;

// ---------------- Logging ----------------
void log_message(const char *msg) {
    printf("%s", msg);
    if (log_file) {
        fprintf(log_file, "%s", msg);
        fflush(log_file);
    }
}

// ---------------- Gestión de clientes ----------------
void add_client(Client client) {
    pthread_mutex_lock(&clients_mutex);
    if (client_count < MAX_CLIENTS) {
        clients[client_count++] = client;
    }
    pthread_mutex_unlock(&clients_mutex);
}

void remove_client(int fd) {
    pthread_mutex_lock(&clients_mutex);
    for (int i = 0; i < client_count; i++) {
        if (clients[i].fd == fd) {
            clients[i] = clients[client_count - 1];
            client_count--;
            break;
        }
    }
    pthread_mutex_unlock(&clients_mutex);
}

// ---------------- Servidor ----------------
#include "client_handler.h"

void start_server(int port, const char *logfile) {
    int sockfd, newfd;
    struct sockaddr_in server_addr, client_addr;
    socklen_t client_len = sizeof(client_addr);
    pthread_t tid;

    log_file = fopen(logfile, "a");

    sockfd = socket(AF_INET, SOCK_STREAM, 0);
    if (sockfd < 0) { perror("socket"); exit(1); }

    server_addr.sin_family = AF_INET;
    server_addr.sin_addr.s_addr = INADDR_ANY;
    server_addr.sin_port = htons(port);

    if (bind(sockfd, (struct sockaddr*)&server_addr, sizeof(server_addr)) < 0) {
        perror("bind"); exit(1);
    }

    if (listen(sockfd, 10) < 0) {
        perror("listen"); exit(1);
    }

    log_message("Server started.\n");

    while (1) {
        newfd = accept(sockfd, (struct sockaddr*)&client_addr, &client_len);
        if (newfd < 0) { perror("accept"); continue; }

        Client client;
        client.fd = newfd;
        client.addr = client_addr;
        client.is_admin = 0;

        add_client(client);
        pthread_create(&tid, NULL, client_thread, &clients[client_count-1]);
    }

    close(sockfd);
    if (log_file) fclose(log_file);
}
