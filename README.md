# FunTools
Tools and Toolchains for FunOS

To build and install the googletest library and headers perform the following steps:

1/ ensure that you have an $(SDK_DIR) directory.  This should generally be a peer of ../FunOS

2/ cd FunTools/Test/googletest/googletest/make

3/ make

4/ make install

5/ the default $(SDK_DIR) is relative to where you checked out ../FunTools. If you have to override, then make install SDK_DIR=path-to-sdk

6/ ls $(SDK_DIR)/include/gtest/*.h and $(SDK_DIR)/lib/gtest.a just to verify everything is there.

Now start writing tests.  This is a great framework.
