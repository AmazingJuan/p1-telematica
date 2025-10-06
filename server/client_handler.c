#include "client_handler.h"
#include "server.h"
#include <stdio.h>
#include <string.h>
#include <unistd.h>
#include <sys/select.h>
#include <sys/time.h>
#include <arpa/inet.h>

#define BUF_SIZE 1024
#define LOGBUF_SIZE 256
#define LOGRESP_SIZE 256
#define LOGREQ_SIZE 256
#define TELEMETRY_INTERVAL 10

extern Car car;
extern pthread_mutex_t car_mutex;


// TELEMETRÍA

void send_telemetry_to_client(Client *client) {
    char buffer[BUF_SIZE];
    char alert[BUF_SIZE];
    int stopped = 0;
    
    // Proteger el acceso al carro con mutex
    pthread_mutex_lock(&car_mutex);
    stopped = car_update(&car);
    car_to_json(&car, buffer, BUF_SIZE);
    
    // Si el carro se detuvo por batería baja, mostrar alerta
    if (stopped) {
        snprintf(alert, sizeof(alert), "ALERT: Car stopped due to low battery (%.2f%%)\n", car.battery);
    }
    
    pthread_mutex_unlock(&car_mutex);
    
    // Enviar alerta a todos

    if (stopped) {
        broadcast(alert, strlen(alert));
        log_message(alert);
    }
    
    send(client->fd, buffer, strlen(buffer), 0);

    char logbuf[LOGBUF_SIZE];
    snprintf(logbuf, sizeof(logbuf), "TELEM to %s:%d: %s", inet_ntoa(client->addr.sin_addr), ntohs(client->addr.sin_port), buffer);
    log_message(logbuf);
}

// COMANDOS DE ADMIN

void process_client_command(Client *client, const char *msg) {

    char buffer[BUF_SIZE];
    char cmd[BUF_SIZE];
    char logreq[LOGREQ_SIZE];
    char logresp[LOGRESP_SIZE];

    strncpy(cmd, msg, BUF_SIZE - 1);
    cmd[BUF_SIZE - 1] = '\0';
    cmd[strcspn(cmd, "\r\n")] = 0;

    snprintf(logreq, sizeof(logreq), "REQ from %s:%d -> %s\n",
            inet_ntoa(client->addr.sin_addr),
            ntohs(client->addr.sin_port),cmd);
    log_message(logreq);

    if (strncmp(cmd, "AUTH ", 5) == 0) {
        const char *password = cmd + 5;
        if (strcmp(password, "admin123") == 0) {
            client->is_admin = 1;
            update_client_admin(client->fd, 1);  // Actualizar en el array global
            const char *ok = "AUTH OK: You are now admin.\n";
            send(client->fd, ok, strlen(ok), 0);

            snprintf(buffer, BUF_SIZE, "Client %s:%d is now admin.\n",
                    inet_ntoa(client->addr.sin_addr),
                    ntohs(client->addr.sin_port));
            log_message(buffer);
            
        } else {
            const char *fail = "AUTH FAIL: Wrong password.\n";
            send(client->fd, fail, strlen(fail), 0);
            log_message("RESP 401 AUTH FAIL\n");
        }
        return;
    }

    if (strncmp(cmd, "LIST USERS", 10) == 0) {
        char out[BUF_SIZE];
        list_users_into(out, sizeof(out));
        send(client->fd, out, strlen(out), 0);
        log_message("RESP LIST USERS sent\n");
        return;
    }

    if (client->is_admin) {

        pthread_mutex_lock(&car_mutex);
        car_command(&car, cmd, buffer, BUF_SIZE);
        pthread_mutex_unlock(&car_mutex);

        send(client->fd, buffer, strlen(buffer), 0);

        snprintf(logresp, sizeof(logresp), "RESP to %s:%d -> %.*s\n", inet_ntoa(client->addr.sin_addr), ntohs(client->addr.sin_port), (int)strcspn(buffer, "\r\n"), buffer);
        log_message(logresp);

    } else {
        const char *err = "ERROR: Not authorized\n";
        send(client->fd, err, strlen(err), 0);
        log_message("RESP 401 Not authorized\n");
    }
}


// HILO DE CLIENTE

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