#ifndef __LIBPCIEPROXY_H__
#define __LIBPCIEPROXY_H__

#include <stdint.h>
#include <stdbool.h>

#ifndef PCIEPROXY_API
#define PCIEPROXY_API
#endif

struct ccu_info_t;

struct ccu_info_t *pcie_csr_init(const char *name, uint64_t offset) PCIEPROXY_API;
void pcie_csr_close(struct ccu_info_t *ccu_info) PCIEPROXY_API;

int pcie_csr_read(struct ccu_info_t *ccu_info,
	 uint64_t base_addr,
	 uint64_t csr_addr,
	 uint64_t *data,
	 uint32_t size) PCIEPROXY_API;

int pcie_csr_write(struct ccu_info_t *ccu_info,
	  uint64_t base_addr,
	  uint64_t csr_addr,
	  uint64_t *data,
	  uint32_t size) PCIEPROXY_API;

void pcie_csr_enable_debug(bool enable) PCIEPROXY_API;

#endif  /* __LIBPCIEPROXY_H__ */
