#include <stdio.h>
#include <stdlib.h>
#include <string.h>

int main(int argc, char *argv[]){
	
	int num = 0;
	printf("You gave me %s\n",argv[1]);
	printf("Enter a number:\n");
	scanf("%d",&num);
	printf("You entered %d\n", num);
	if (num == 72){
		printf("You entered a magical number (72)\n");
		if (strcpy(argv[1], "magic!!~woo")){
			printf("even more magic! yay\n");
		}
	}

	printf("whelp, we got to the end :)\n");

	return EXIT_SUCCESS;
}
