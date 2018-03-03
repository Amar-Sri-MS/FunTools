/*
 *  csr_gen.cpp
 *
 *  !!!!AUTOGENERATED!!! DO NOT EDIT !!!!
 *
 *  Copyright 2018 Fungible Inc. All rights reserved.
 */

#include "csr.h"

F1NS::F1NS() {
    /*
     * First create all the CSRs
     */
    fld_map_t rand_csr_0 {
        CREATE_ENTRY("mac_learning_en", 0, 1),
        CREATE_ENTRY("port_blocked", 1, 1),
        CREATE_ENTRY("fl_rsvd0", 2, 1),
        CREATE_ENTRY("fl_rsvd1", 3, 1),
        CREATE_ENTRY("__pad0", 4, 4),
        CREATE_ENTRY("__rsvd", 8, 56)
    };

    fld_map_t rand_csr_1 {
        CREATE_ENTRY("learn_en", 0, 1),
        CREATE_ENTRY("port_bl", 1, 1),
        CREATE_ENTRY("fl_rsvd0", 2, 1),
        CREATE_ENTRY("fl_rsvd1", 3, 1),
        CREATE_ENTRY("__pad0", 4, 4),
        CREATE_ENTRY("__rsvd", 8, 56)
    };
    /*
     * Create all the ring collections
     */

    ring_coll_t nu_rng;
    nu_rng.add_ring(0, 0x1200000000);
    nu_rng.add_ring(1, 0x3400000000);

    /*
     * Add all the address nodes, encode path
     */

    auto p = nu_rng[0].add_an({"TEST_0", "rand_0"}, 0x33445566);

    auto q = nu_rng[0].add_an({"TEST_0", "rand_1"}, 0x223344);

    /*
     * Create CSR signatures
     */
    auto csr_0 = csr_grp_t(
            std::make_shared<csr_s>(rand_csr_0),
            0x22,
            CSR_TYPE::REG);

    auto csr_1 = csr_grp_t(
            std::make_shared<csr_s>(rand_csr_1),
            0x44,
            CSR_TYPE::REG);
    /*
     * Add the CSRs
     */

    add_csr(p, "rand_csr_0", csr_0);
    add_csr(q, "rand_csr_1", csr_1);

    /*
     * Finally, add them to the top level tree
     */
    sys_rings["NU"] = nu_rng;

}
