
all: compare endure

compare: compare.c
	gcc -O2 -Wall -o compare compare.c
	strip compare

endure: endure.c
	gcc -O2 -Wall -o endure endure1.c -lpthread
	strip endure

clean:
	rm -f endure compare

