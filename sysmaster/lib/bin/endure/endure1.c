#define _XOPEN_SOURCE 600
#include <stdio.h>
#include <stdlib.h>
#include <sys/types.h>
#include <sys/stat.h>
#include <fcntl.h>
#include <pthread.h>
#include <malloc.h>
#include <unistd.h>
#include <string.h>

#define O_DIRECT 040000

volatile int stop=0;

char *golden=NULL;

typedef struct {
  int fd;
  long block;
} info_t;

void hexdump(char *golden, char *read)
{
  printf("------------\n");
  int i, j;
  for (i=0; i<256; i++) {
    for (j=0; j<16; j++) printf("%02x ", golden[i*16+j]&255);
    printf(" ---- ");
    for (j=0; j<16; j++) printf("%02x ", read[i*16+j]&255);
    printf("\n");
  }
  printf("------------\n");
}

void *doit(void *ptr)
{
  info_t *info = (info_t*)ptr;
  void *buff;
  if (posix_memalign(&buff, 4096, 4096)) { perror("Unable to allocate memory thread\n"); exit(2); }

  unsigned long loops = 0;
  while (pread(info->fd, buff, 4096, 4096*info->block)==4096) {
    if (memcmp(buff, golden, 4096)) { printf("Data error detected thread %ld @ loop %ld\n", info->block, loops); hexdump(golden, buff); break; }
    loops++;
    if (loops%1000==0) { printf("Block %ld --  %ld loops\n", info->block, loops); }
  }
  
  printf("Failed read for block %ld @ loop %ld!!!\n", info->block, loops);
  stop = 1;

  pthread_exit((void*)1); //Should never get here
}


int main(int argc, char **argv)
{
  if (argc!=2) {printf("Usage:  %s /dev/vgc[a...z]0\n", argv[0]); exit(3); }

  int fd = open(argv[1], O_RDWR|O_DIRECT);
  if (fd<0) { perror("Unable to open file"); exit(1); }

  char *buff;
  if (posix_memalign((void*)&buff, 4096, 4096)) { perror("Unable to allocate memory main\n"); exit(2); }
  if (posix_memalign((void*)&golden, 4096, 4096)) { perror("Unable to allocate memory main\n"); exit(2); }
  
  long i;
  for (i=0; i<4096; i++) golden[i] = rand() & 255;
  
  for (i=0; i<4096; i++) if (pwrite(fd, golden, 4096, 4096*i)!=4096) { perror("Unable to write file...\n"); exit(4); }
  
  //closing fd,since service vgcd stop will not work
  close(fd);
  // restarting service Bug 20742, where read should not come from EU cache
  int ret;
  ret = system("service vgcd restart");
  if (ret != 0 ) { printf("Failed to do service restart,rc = %i\n",ret); exit(2);}
  
  // reopeining the fd
  fd = open(argv[1], O_RDWR|O_DIRECT);
  if (fd<0) { perror("Unable to open file"); exit(1); }

  for (i=0; i<128; i++) {
    pthread_t x;
    info_t *info = (info_t*)malloc(sizeof(info_t));
    info->fd = fd;
    info->block = i;
    pthread_create(&x, NULL, doit, info);
  }

  // 128 reader threads going, main thread to loop forever reading over and over
  unsigned long loops=0;
  while (!stop) {
    for (i=0; i<4096; i++) {
      if (pread(fd, buff, 4096, 4096*i)!=4096) { printf("Read failed block %ld @ loop %ld\n", i, loops); stop=1; break; }
      else if (memcmp(buff, golden, 4096)) { printf("Data error detected main thread block %ld @ loop %ld\n", i, loops); hexdump(golden, buff); stop=1; break; }
    }
    loops++;
    if (loops%1000==0) { printf("Main --  %ld loops\n", loops);}
  }

  return 0;
}

