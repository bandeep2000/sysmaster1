#include <stdio.h>
#include <stdlib.h>
#include <string.h>

int main(int argc, char**argv)
{
  if (argc!=2) {printf("usage:  %s /dev/vgc[a...z]0\n", argv[0]); exit(3); }
  FILE *fp = fopen(argv[0], "rb");
  char orig[4096];
  char new[4096];
  fread(orig, 4096, 1, fp);
  long i;
  long err =0;
  for (i=1; i<4096; i++) {
    fread(new, 4096, 1, fp);
    if (!memcmp(new, orig, 4096)) { printf("Mismatch @ block %ld\n", i); err++; }
  }
  return (err>0)?1:0;
}

