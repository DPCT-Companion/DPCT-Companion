
        void* ptr       = nullptr;
        /*
        DPCT1003:15: Migrated API does not return error code. (*, 0) is
        inserted. You may need to rewrite this code.
        */
        GW_CU_CHECK_ERR((ptr = (void *)sycl::malloc_device(n * sizeof(T),
                                                     dpct::get_default_queue()),
                   0));

        /*
        DPCT1003:15: Migrated API does not return error code. (*, 0) is
        inserted. You may need to rewrite this code.
        */
        GW_CU_CHECK_ERR((ptr = (void *)sycl::malloc_device(n * sizeof(T),
                                                     dpct::get_default_queue()),
                   0));
        /*
        DPCT1015:63: Output needs adjustment.
        */
        stream_ct1 << "assert: lhs=%d, rhs=%d\n";
