CC=gcc
CFLAGS=-Wall -Wextra -O2 -pthread
SRC=main.c server.c client_handler.c car.c
OBJ=$(SRC:.c=.o)
BIN=server

all: $(BIN)
$(BIN): $(OBJ)
	$(CC) $(CFLAGS) -o $@ $(OBJ)
%.o: %.c
	$(CC) $(CFLAGS) -c $<
clean:
	rm -f $(OBJ) $(BIN)