device_matrix_view<nw_score_t> scores = s->get_matrix_view(id, bw, n + m);
    ukkonen_init_score_matrix(scores, k, p, item_ct1);
    /*
    DPCT1065:186: Consider replacing sycl::nd_item::barrier() with
    sycl::nd_item::barrier(sycl::access::fence_space::local_space) for better
    performance if there is no access to global memory.
    */
    item_ct1.barrier();
    if (p % 2 == 0)
    {
        for (int lx = 0; lx < 2 * max_cols; ++lx)
        {
            ukkonen_compute_score_matrix_even(scores, kmax_even, k, m, n, query,
                                              target, max_target_query_length,
                                              p, 2 * lx, item_ct1);
            /*
            DPCT1065:189: Consider replacing sycl::nd_item::barrier() with
            sycl::nd_item::barrier(sycl::access::fence_space::local_space) for
            better performance if there is no access to global memory.
            */
            item_ct1.barrier();
            ukkonen_compute_score_matrix_odd(scores, kmax_odd, k, m, n, query,
                                             target, max_target_query_length, p,
                                             2 * lx + 1, item_ct1);
            /*
            DPCT1065:190: Consider replacing sycl::nd_item::barrier() with
            sycl::nd_item::barrier(sycl::access::fence_space::local_space) for
            better performance if there is no access to global memory.
            */
            item_ct1.barrier();
        }
    }