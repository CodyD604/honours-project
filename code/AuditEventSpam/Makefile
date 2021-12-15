CC=gcc
OBJ=eventSpam.o
LDFLAGS=-pthread

eventSpam: $(OBJ)
	$(CC) $(CFLAGS) $(OBJ) -o $@ $(LDFLAGS)

.PHONY: clean

clean:
	rm -f ./*.o ./eventSpam