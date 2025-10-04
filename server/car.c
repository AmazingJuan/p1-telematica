#include "car.h"
#include <stdio.h>
#include <string.h>

void car_init(Car *c) {
    c->speed = 0;
    c->battery = 100;
    c->temperature = 25;
    strcpy(c->direction, "STOP");
}

void car_update(Car *c) {
    // Simular cambios en telemetría
    if (c->speed > 0) c->battery -= 0.1;
    if (c->battery < 0) c->battery = 0;
}

void car_command(Car *c, const char *cmd, char *response, int bufsize) {
    if (strncmp(cmd, "SPEED UP", 8) == 0) {
        c->speed = c->speed + 10;
        snprintf(response, bufsize, "Speed increased to %.2f\n", c->speed);
    } else if (strncmp(cmd, "SLOW DOWN", 9) == 0) {
        c->speed = c->speed - 10;
        if (c->speed < 0) c->speed = 0;
        snprintf(response, bufsize, "Speed decreased to %.2f\n", c->speed);
    } else if (strncmp(cmd, "TURN LEFT", 9) == 0) {
        strcpy(c->direction, "LEFT");
        snprintf(response, bufsize, "Turned LEFT\n");
    } else if (strncmp(cmd, "TURN RIGHT", 10) == 0) {
        strcpy(c->direction, "RIGHT");
        snprintf(response, bufsize, "Turned RIGHT\n");
    } else {
        snprintf(response, bufsize, "Unknown command\n");
    }
}

void car_to_json(Car *c, char *buffer, int bufsize) {
    snprintf(buffer, bufsize,
             "{\"speed\":%.2f,\"battery\":%.2f,\"temperature\":%.2f,\"direction\":\"%s\"}\n",
             c->speed, c->battery, c->temperature, c->direction);
}
