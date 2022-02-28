        /*
        DPCT1023:66: The DPC++ sub-group does not support mask options for
        sycl::shift_group_right.
        */
        uint32_t x =
                    sycl::shift_group_right(item_ct1.get_sub_group(), carry, 1);


        /*
        DPCT1023:67: The DPC++ sub-group does not support mask options for
        sycl::shift_group_right.
        */
        const int32_t mv = sycl::shift_group_left(item_ct1.get_sub_group(), cur_min, i);