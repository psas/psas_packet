#include <stdio.h>
#include <string.h>
#include <arpa/inet.h>

typedef struct {
	char     ID[4];
	uint8_t  timestamp[6];
	uint16_t data_length;
} __attribute__((packed)) message_header;

int main(int argc, char **argv)
{
	message_header header;

	if(argc < 2)
	{
		fprintf(stderr, "Usage: %s <ID>\n", argv[0]);
		return 1;
	}

	while(fread(&header, sizeof header, 1, stdin) == 1)
	{
		uint16_t length = ntohs(header.data_length);
		char buf[1024];
		fread(buf, 1, length, stdin);
		if(!memcmp(header.ID, argv[1], sizeof header.ID))
			fwrite(buf, 1, length, stdout);
	}

	return 0;
}
