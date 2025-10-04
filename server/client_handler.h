#ifndef CLIENT_HANDLER_H
#define CLIENT_HANDLER_H

#include <stddef.h>
#include "car.h"
#include <netinet/in.h>

typedef struct {int fd; struct sockaddr_in addr; int is_admin;} Client;

// hilo por cliente

void *client_thread(void *arg);

// funciones de ayuda para los clientes

void send_telemetry_to_client(Client *client);
void process_client_command(Client *client, const char *msg);

#endif