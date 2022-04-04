/*
   Shared memory speeds up performance when we need to access data frequently. 
   Here, the 1D stencil kernel adds all its neighboring data within a radius.

   The C model is added to verify the stencil result on a GPU
 */

#include <CL/sycl.hpp>
#include <dpct/dpct.hpp>
#include <stdio.h>
#include <stdlib.h>

#define LENGTH 1024
#define THREADS_PER_BLOCK 256
#define RADIUS 7
#define BLOCK_SIZE THREADS_PER_BLOCK

void stencil_1d(int *in, int *out, sycl::nd_item<3> item_ct1, int *temp) {

  int gindex = item_ct1.get_local_id(2) +
               item_ct1.get_group(2) * item_ct1.get_local_range().get(2);
  int lindex = item_ct1.get_local_id(2) + RADIUS;

  // Read input elements into shared memory
  temp[lindex] = in[gindex];

  // At both end of a block, the sliding window moves beyond the block boundary.
  if (item_ct1.get_local_id(2) < RADIUS) {
    temp[lindex - RADIUS] = (gindex < RADIUS) ? 0 : in[gindex - RADIUS];
    temp[lindex + BLOCK_SIZE] = in[gindex + BLOCK_SIZE];
  }

  // Synchronize (ensure all the threads will be completed before continue)
  item_ct1.barrier(sycl::access::fence_space::local_space);

  // Apply the 1D stencil
  int result = 0;
  for (int offset = -RADIUS ; offset <= RADIUS ; offset++)
    result += temp[lindex + offset];

  // Store the result
  out[gindex] = result; 
}

int main(void) {
  dpct::device_ext &dev_ct1 = dpct::get_current_device();
  sycl::queue &q_ct1 = dev_ct1.default_queue();
  int size = LENGTH * sizeof(int);
  int pad_size = (LENGTH + RADIUS) * sizeof(int);

  int *a, *b;
  // Alloc space for host copies of a, b, c and setup input values
  a = (int *)malloc(pad_size); 
  b = (int *)malloc(size);

  for (int i = 0; i < LENGTH+RADIUS; i++) a[i] = i;

  int *d_a, *d_b;
  // Alloc space for device copies of a, b, c
  d_a = (int *)sycl::malloc_device(pad_size, q_ct1);
  d_b = (int *)sycl::malloc_device(size, q_ct1);

  // Copy inputs to device
  q_ct1.memcpy(d_a, a, pad_size).wait();

  // Launch add() kernel on GPU
  q_ct1.submit([&](sycl::handler &cgh) {
    sycl::accessor<int, 1, sycl::access_mode::read_write,
                   sycl::access::target::local>
        temp_acc_ct1(sycl::range<1>(270 /*BLOCK_SIZE + 2 * RADIUS*/), cgh);

    cgh.parallel_for(
        sycl::nd_range<3>(sycl::range<3>(1, 1, LENGTH / THREADS_PER_BLOCK) *
                              sycl::range<3>(1, 1, THREADS_PER_BLOCK),
                          sycl::range<3>(1, 1, THREADS_PER_BLOCK)),
        [=](sycl::nd_item<3> item_ct1) {
          stencil_1d(d_a, d_b, item_ct1, temp_acc_ct1.get_pointer());
        });
  });

  // Copy result back to host
  q_ct1.memcpy(b, d_b, size).wait();

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
  sycl::free(d_a, q_ct1);
  sycl::free(d_b, q_ct1);
  return 0;
}
