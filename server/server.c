#include "server.h"
#include "client_handler.h"
#include "car.h"
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <pthread.h>
#include <unistd.h>
#include <arpa/inet.h>

static Client clients[MAX_CLIENTS];
static int client_count = 0;
static pthread_mutex_t clients_mutex = PTHREAD_MUTEX_INITIALIZER;

// ESTADO DEL CARRO

Car car; // Instancia del carro 
pthread_mutex_t car_mutex = PTHREAD_MUTEX_INITIALIZER;

// LOGGING

static FILE *log_file = NULL;

void log_message(const char *msg) {
    printf("%s", msg);
    if (log_file) {
        fprintf(log_file, "%s", msg);
        fflush(log_file);
    }
}

// GESTIÓN DE CLIENTES

void add_client(Client client) { // Añade un cliente a la lista de clientes

    pthread_mutex_lock(&clients_mutex);
    if (client_count < MAX_CLIENTS) {
        clients[client_count++] = client;
    }
    pthread_mutex_unlock(&clients_mutex);
}

void remove_client(int fd) { // Elimina un cliente de la lista de clientes

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

void update_client_admin(int fd, int is_admin) { // Actualiza el estado de admin de un cliente

    pthread_mutex_lock(&clients_mutex);
    for (int i = 0; i < client_count; i++) {
        if (clients[i].fd == fd) {
            clients[i].is_admin = is_admin;
            break;
        }
    }
    pthread_mutex_unlock(&clients_mutex);
}

void list_users_into(char *out, size_t n) { // Lista los usuarios

    pthread_mutex_lock(&clients_mutex);
    int used = snprintf(out, n, "USERS %d:", client_count);
    for (int i = 0; i < client_count && used < (int)n; i++) {
        char temp[64];
        snprintf(temp, sizeof(temp), " [%s:%d%s]",
                 inet_ntoa(clients[i].addr.sin_addr),
                 ntohs(clients[i].addr.sin_port),
                 clients[i].is_admin ? " ADMIN" : " OBS");
        used = used + snprintf(out + used, n - used, "%s", temp);
    }
    used = used + snprintf(out + used, n - used, "\n");
    pthread_mutex_unlock(&clients_mutex);
}

void broadcast(const char *data, size_t len) { // Envía un mensaje a todos los clientes
    pthread_mutex_lock(&clients_mutex);
    for (int i = 0; i < client_count; i++) {
        send(clients[i].fd, data, len, 0);
    }
    pthread_mutex_unlock(&clients_mutex);
}


// SERVIDOR

void start_server(int port, const char *logfile) { // Inicia el servidor

    int sockfd, newfd;
    struct sockaddr_in server_addr, client_addr;
    socklen_t client_len = sizeof(client_addr);
    pthread_t tid;

    log_file = fopen(logfile, "a");

    sockfd = socket(AF_INET, SOCK_STREAM, 0);
    if (sockfd < 0) { perror("socket"); exit(1); }

    int opt = 1;
    setsockopt(sockfd, SOL_SOCKET, SO_REUSEADDR, &opt, sizeof(opt));

    server_addr.sin_family = AF_INET;
    server_addr.sin_addr.s_addr = INADDR_ANY;
    server_addr.sin_port = htons(port);

    if (bind(sockfd, (struct sockaddr*)&server_addr, sizeof(server_addr)) < 0) {
        perror("bind"); exit(1);
    }

    if (listen(sockfd, 10) < 0) {
        perror("listen"); exit(1);
    }

    car_init(&car);
    log_message("Server started.\n");
    log_message("Car initialized.\n");

    while (1) {
        newfd = accept(sockfd, (struct sockaddr*)&client_addr, &client_len);
        if (newfd < 0) { 
            perror("accept");
            continue;
        }

        Client client;
        client.fd = newfd;
        client.addr = client_addr;
        client.is_admin = 0;

        add_client(client);
        pthread_create(&tid, NULL, client_thread, &clients[client_count-1]);
        pthread_detach(tid);
    }

    close(sockfd);
    if (log_file) fclose(log_file);
}