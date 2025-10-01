#include "client_handler.h"
#include <stdio.h>
#include <string.h>
#include <unistd.h>
#include <sys/select.h>
#include <sys/time.h>
#include <arpa/inet.h>

#define BUF_SIZE 1024
#define TELEMETRY_INTERVAL 10

extern Car car;
extern FILE *log_file;

// ---------------- Telemetría ----------------
void send_telemetry_to_client(Client *client) {
    char buffer[BUF_SIZE];
    car_update(&car);
    car_to_json(&car, buffer, BUF_SIZE);
    send(client->fd, buffer, strlen(buffer), 0);
}

// ---------------- Comandos ----------------
void process_client_command(Client *client, const char *msg) {
    char buffer[BUF_SIZE];

    if (strncmp(msg, "AUTH ", 5) == 0) {
        char *password = (char *)(msg + 5);
        password[strcspn(password, "\r\n")] = 0;

        if (strcmp(password, "admin123") == 0) {
            client->is_admin = 1;
            send(client->fd, "AUTH OK: You are now admin.\n", 29, 0);
            snprintf(buffer, BUF_SIZE, "Client %s:%d is now admin.\n",
                     inet_ntoa(client->addr.sin_addr),
                     ntohs(client->addr.sin_port));
            log_message(buffer);
        } else {
            send(client->fd, "AUTH FAIL: Wrong password.\n", 27, 0);
        }
    }
    else if (client->is_admin) {
        car_command(&car, msg, buffer, BUF_SIZE);
        send(client->fd, buffer, strlen(buffer), 0);
    } else {
        send(client->fd, "ERROR: Not authorized\n", 22, 0);
    }
}

// ---------------- Hilo de cliente ----------------
void *client_thread(void *arg) {
    Client *client_ptr = (Client*)arg;
    Client client = *client_ptr;
    char buffer[BUF_SIZE];
    int n;

    snprintf(buffer, BUF_SIZE, "Client connected: %s:%d\n",
             inet_ntoa(client.addr.sin_addr),
             ntohs(client.addr.sin_port));
    log_message(buffer);

    send(client.fd, "You are observer by default. Send AUTH <password> to become admin.\n", 70, 0);

    struct timeval last_telemetry;
    gettimeofday(&last_telemetry, NULL);

    while (1) {
        fd_set read_fds;
        FD_ZERO(&read_fds);
        FD_SET(client.fd, &read_fds);

        struct timeval now, timeout, elapsed;
        gettimeofday(&now, NULL);
        timersub(&now, &last_telemetry, &elapsed);

        if (elapsed.tv_sec >= TELEMETRY_INTERVAL) {
            send_telemetry_to_client(&client);
            gettimeofday(&last_telemetry, NULL);
            timeout.tv_sec = TELEMETRY_INTERVAL;
            timeout.tv_usec = 0;
        } else {
            timeout.tv_sec = TELEMETRY_INTERVAL - elapsed.tv_sec;
            timeout.tv_usec = 0;
        }

        int ret = select(client.fd + 1, &read_fds, NULL, NULL, &timeout);
        if (ret > 0 && FD_ISSET(client.fd, &read_fds)) {
            n = recv(client.fd, buffer, BUF_SIZE - 1, 0);
            if (n <= 0) break;
            buffer[n] = '\0';
            process_client_command(&client, buffer);
        }
    }

    snprintf(buffer, BUF_SIZE, "Client disconnected: %s:%d\n",
             inet_ntoa(client.addr.sin_addr),
             ntohs(client.addr.sin_port));
    log_message(buffer);

    close(client.fd);
    remove_client(client.fd);

    pthread_exit(NULL);
}
