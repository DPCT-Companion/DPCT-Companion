/*
   Shared memory speeds up performance when we need to access data frequently.
   Here, the 1D stencil kernel adds all its neighboring data within a radius.

   The C model is added to verify the stencil result on a GPU
 */

#include <stdio.h>
#include <stdlib.h>
#include <cuda.h>

#define LENGTH 1024
#define THREADS_PER_BLOCK 256
#define RADIUS 7
#define BLOCK_SIZE THREADS_PER_BLOCK

__global__ void stencil_1d(int *in, int *out) {
  __shared__ int temp[BLOCK_SIZE + 2 * RADIUS];
  int gindex = threadIdx.x + blockIdx.x * blockDim.x;
  int lindex = threadIdx.x + RADIUS;

  // Read input elements into shared memory
  temp[lindex] = in[gindex];

  // At both end of a block, the sliding window moves beyond the block boundary.
  if (threadIdx.x < RADIUS) {
    temp[lindex - RADIUS] = (gindex < RADIUS) ? 0 : in[gindex - RADIUS];
    temp[lindex + BLOCK_SIZE] = in[gindex + BLOCK_SIZE];
  }

  // Synchronize (ensure all the threads will be completed before continue)
  __syncthreads();

  // Apply the 1D stencil
  int result = 0;
  for (int offset = -RADIUS ; offset <= RADIUS ; offset++)
    result += temp[lindex + offset];

  // Store the result
  out[gindex] = result;
}



int main(void) {
  int size = LENGTH * sizeof(int);
  int pad_size = (LENGTH + RADIUS) * sizeof(int);

  int *a, *b;
  // Alloc space for host copies of a, b, c and setup input values
  a = (int *)malloc(pad_size);
  b = (int *)malloc(size);

  for (int i = 0; i < LENGTH+RADIUS; i++) a[i] = i;

  int *d_a, *d_b;
  // Alloc space for device copies of a, b, c
  cudaMalloc((void **)&d_a, pad_size);
  cudaMalloc((void **)&d_b, size);

  // Copy inputs to device
  cudaMemcpy(d_a, a, pad_size, cudaMemcpyHostToDevice);

  // Launch add() kernel on GPU
  stencil_1d <<< dim3(LENGTH/THREADS_PER_BLOCK), dim3(THREADS_PER_BLOCK) >>> (d_a, d_b);

  // Copy result back to host
  cudaMemcpy(b, d_b, size, cudaMemcpyDeviceToHost);

  // verification
  bool ok = true;
  for (int i = 0; i < 2*RADIUS; i++) {
    int s = 0;
    for (int j = i; j <= i+2*RADIUS; j++)
      s += j < RADIUS ? 0 : (a[j] - RADIUS);
    if (s != b[i]) {
      printf("Error at %d: %d (host) != %d (device)\n", i, s, b[i]);
      ok = false;
      break;
    }
  }

  for (int i = 2*RADIUS; i < LENGTH; i++) {
    int s = 0;
    for (int j = i-RADIUS; j <= i+RADIUS; j++)
      s += a[j];
    if (s != b[i]) {
      printf("Error at %d: %d (host) != %d (device)\n", i, s, b[i]);
      ok = false;
      break;
    }
  }
  printf("%s\n", ok ? "PASS" : "FAIL");

  // Cleanup
  free(a);
  free(b);
  cudaFree(d_a);
  cudaFree(d_b);
  return 0;
}
