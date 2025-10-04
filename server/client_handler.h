#ifndef CLIENT_HANDLER_H
#define CLIENT_HANDLER_H

#include <stddef.h>
#include "server.h"
#include "car.h"

// hilo por cliente

void *client_thread(void *arg);

void send_telemetry_to_client(Client *client);
void process_client_command(Client *client, const char *msg);

#endif