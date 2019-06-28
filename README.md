# FunTools
Tools and Toolchains for FunOS

To build and install the googletest library and headers perform the following steps:

1/ ensure that you have an $(SDKDIR) directory.  This should generally be a peer of ../FunOS

2/ cd FunTools/Test/googletest/googletest/make

3/ make

4/ make install

5/ the default $(SDKDIR) is relative to where you checked out ../FunTools. If you have to override, then make install SDKDIR=path-to-sdk

6/ Check $(SDKDIR)/include/gtest/*.h and $(SDKDIR)/lib/gtest.a just to verify the install

7/ To build FunOS with gtest test cases, run "make GTEST=1"

8/ To test, run "build/funos-posix --gtest_filter="*" --gtest_repeat=2

Now start writing tests !  This is a great framework.
