#include "car.h"
#include <stdio.h>
#include <string.h>
#include <stdlib.h>
#include <time.h>

void car_init(Car *c) { // Inicializa el carro con valores por defecto
    c->speed = 0;
    c->battery = 100;
    c->temperature = 25;
    strcpy(c->direction, "STOP");
    
    // Inicializar generador de números aleatorios para temperatura ambiente
    srand(time(NULL));
}

int car_update(Car *c) { // Actualiza el estado del carro
    int stopped_by_battery = 0;
    
    // Actualizar batería
    if (c->speed > 0) {
        c->battery -= 5.0;
    } else {
        c->battery -= 1.0;
    }
    
    if (c->battery < 0){
        c->battery = 0;
    }
    
    // Simular temperatura ambiente con variaciones aleatorias

    const double MIN_TEMP = 15.0;
    const double MAX_TEMP = 35.0;
    
    // Generar cambio aleatorio

    double temp_change = ((double)rand() / RAND_MAX) * 0.6 - 0.3;
    c->temperature += temp_change;
    
    if (c->temperature < MIN_TEMP) {
        c->temperature = MIN_TEMP;
    } else if (c->temperature > MAX_TEMP) {
        c->temperature = MAX_TEMP;
    }
    
    // Detener carro si batería baja
    
    if (c->battery < 10.0 && c->speed > 0) {
        c->speed = 0;
        strcpy(c->direction, "STOP");
        stopped_by_battery = 1;
    }
    
    return stopped_by_battery;
}

void car_command(Car *c, const char *cmd, char *response, int bufsize) { // Comandos que recibe el Carro
    
    // Comando de recarga de batería
    if (strncmp(cmd, "RECHARGE BATTERY", 16) == 0) {
        c->battery = 100.0;
        snprintf(response, bufsize, "Battery recharged to 100%%\n");
        return;
    }
    
    // Si la batería es menor a 10%, no permitir comandos

    if (c->battery < 10.0) {
        snprintf(response, bufsize, "ERROR: Battery too low (%.2f%%). Cannot execute commands. Please RECHARGE BATTERY.\n", c->battery);
        return;
    }
    
    // Comandos de movimiento
    
    if (strncmp(cmd, "SPEED UP", 8) == 0) {
        c->speed = c->speed + 10;
        if (strcmp(c->direction, "STOP") == 0) {
            strcpy(c->direction, "FORWARD");
        }
        snprintf(response, bufsize, "Speed increased to %.2f\n", c->speed);
    } else if (strncmp(cmd, "SLOW DOWN", 9) == 0) {
        c->speed = c->speed - 10;
        if (c->speed < 0) c->speed = 0;

        if (c->speed == 0) {
            strcpy(c->direction, "STOP");
        }

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
    snprintf(buffer, bufsize, "{\"speed\":%.2f,\"battery\":%.2f,\"temperature\":%.2f,\"direction\":\"%s\"}\n", c->speed, c->battery, c->temperature, c->direction);
}