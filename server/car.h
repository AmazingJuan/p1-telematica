#ifndef CAR_H
#define CAR_H

typedef struct {
    float speed;
    float battery;
    float temperature;
    char direction[16];
} Car;

void car_init(Car *c);
int car_update(Car *c);
void car_command(Car *c, const char *cmd, char *response, int bufsize);
void car_to_json(Car *c, char *buffer, int bufsize);

#endif