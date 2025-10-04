#ifndef SERVER_H
#define SERVER_H

#include <netinet/in.h>
#include <pthread.h>
#include <stdio.h>

#define MAX_CLIENTS 50

typedef struct {int fd; struct sockaddr_in addr; int is_admin;} Client;

// logging
void log_message(const char *msg);

// gestión de clientes

void add_client(Client client);
void remove_client(int fd);
void update_client_admin(int fd, int is_admin);
void broadcast(const char *data, size_t len);
void list_users_into(char *out, size_t n);

// arranque del servidor

void start_server(int port, const char *logfile);

#endif