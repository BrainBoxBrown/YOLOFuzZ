#include <stdio.h>
#include <stdlib.h>
#include <string.h>

int main(int argc, char *argv[]){
	
	char buf[10];
	memcpy(buf,argv[1],strlen(argv[1]));
	printf("%s\n", buf);
	return EXIT_SUCCESS;
}
