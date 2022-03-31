create_buffer(size_t buffer_size) try {
        // shared_ptr creation packed in a function so it can be used in constructor's initilaization list
        void* ptr = nullptr;
        /*
        DPCT1003:10: Migrated API does not return error code. (*, 0) is
        inserted. You may need to rewrite this code.
        */
        GW_CU_CHECK_ERR((ptr = (void *)sycl::malloc_device(
                             buffer_size, dpct::get_default_queue()),
                         0));
        auto ret_val = std::unique_ptr<char, void (*)(char *)>(
            static_cast<char *>(ptr), [](char *ptr) {
                                                                  /*
                                                                  DPCT1003:11:
                                                                  Migrated API
                                                                  does not
                                                                  return error
                                                                  code. (*, 0)
                                                                  is inserted.
                                                                  You may need
                                                                  to rewrite
                                                                  this code.
                                                                  */
                                                                  /*
                                                                  DPCT1003:30:
                                                                  Migrated API
                                                                  does not
                                                                  return error
                                                                  code. (*, 0)
                                                                  is inserted.
                                                                  You may need
                                                                  to rewrite
                                                                  this code.
                                                                  */
                                                                  /*
                                                                  DPCT1003:60:
                                                                  Migrated API
                                                                  does not
                                                                  return error
                                                                  code. (*, 0)
                                                                  is inserted.
                                                                  You may need
                                                                  to rewrite
                                                                  this code.
                                                                  */
                                                                  try
                                                                  {
                                                              GW_CU_ABORT_ON_ERR((
                                                                  sycl::free(
                                                                      ptr,
                                                                      dpct::
                                                                          get_default_queue()),
                                                                  0));
                                                              }
                                                              catch (sycl::exception const &exc) {
                                                                std::cerr
                                                                    << exc.what()
                                                                    << "Excepti"
                                                                       "on "
                                                                       "caught "
                                                                       "at "
                                                                       "file:"
                                                                    << __FILE__
                                                                    << ", line:"
                                                                    << __LINE__
                                                                    << std::
                                                                           endl;
                                                                std::exit(1);
                                                              }
            });
        return ret_val;
    }
    catch (sycl::exception const &exc) {
      std::cerr << exc.what() << "Exception caught at file:" << __FILE__
                << ", line:" << __LINE__ << std::endl;
      std::exit(1);
    }