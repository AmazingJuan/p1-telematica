#ifndef CLIENT_HANDLER_H
#define CLIENT_HANDLER_H

#include "server.h"
#include "car.h"

// Función que maneja cada cliente
void *client_thread(void *arg);

// Envía telemetría a un cliente
void send_telemetry_to_client(Client *client);

// Procesa un comando recibido de cliente
void process_client_command(Client *client, const char *msg);

#endif
