#ifndef SERVER_H
#define SERVER_H

#include "client_handler.h"

#define MAX_CLIENTS 50
#define LOG_FILE "server.log"

// Inicializa y arranca el servidor
void start_server(int port, const char *logfile);

// Logging
void log_message(const char *msg);

// Gestión de clientes
typedef struct {
    int fd;
    struct sockaddr_in addr;
    int is_admin;
} Client;

void add_client(Client client);
void remove_client(int fd);

#endif
