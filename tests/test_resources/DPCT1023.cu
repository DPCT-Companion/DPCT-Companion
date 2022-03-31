        uint32_t x = __shfl_up_sync(warp_mask, carry, 1);

        const int32_t mv = __shfl_down_sync(0xffff'ffffu, cur_min, i);