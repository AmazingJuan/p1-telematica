#include "server.h"

int main(int argc, char *argv[]) {
    if (argc < 3) {
        printf("Usage: %s <port> <logfile>\n", argv[0]);
        return 1;
    }

    int port = atoi(argv[1]);
    const char *logfile = argv[2];

    start_server(port, logfile);

    return 0;
}
