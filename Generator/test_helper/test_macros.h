// Various macros for testing alignment and size of structs in C
// code.
//
// Used for testing structs created by Generator.
//
// Copyright Fungible Inc. 2017.

// TODO(bowdidge): Switch to gtest.
#define ASSERT_SIZE(var, bytes, varStr)					\
  { \
    if (sizeof(var) != (bytes)) {					\
      fprintf(stderr,							\
	      "%s:%d: FAIL: %s structure expected to be %" PRIu64	\
	      " bytes, got %" PRIu64 "\n",				\
	      __FILE__, __LINE__,					\
	      (varStr), (uint64_t) (bytes), (uint64_t) sizeof(var));	\
    } \
  }

#define ASSERT_OFFSET(var, field, offset, varStr)			\
  {									\
    if (offsetof(var, field) !=offset) {				\
      fprintf(stderr,							\
	      "%s:%d: FAIL: %s structure expected to be %"		\
	      PRIu64 " bytes, got %" PRIu64 "\n",			\
	      __FILE__, __LINE,						\
	      varStr, (uint64_t) offset,				\
	      (uint64_t) offsetof(var, field));				\
      exit(1);								\
  }    

#define ASSERT_EQUAL(expected_value, gotten_value, msg)			\
  if ((expected_value) != (gotten_value)) {				\
    fprintf(stderr, "%s:%d: FAIL: %s: Expected %" PRIu64 ", got %" PRIu64 "\n", \
	    __FILE__, __LINE__,						\
	    msg, (uint64_t) (expected_value), (uint64_t) (gotten_value)); \
    exit(1);								\
  }

#define ASSERT_TRUE(gotten_value, msg)				\
  if (!(gotten_value)) {					\
    fprintf(stderr, "%s:%d: FAIL: %s: Expression not true.\n",	\
	    __FILE__, __LINE__, msg);				\
  }

