/*
 *      MCTP Daemon - FC mctp slave implementation
 *      Copyright © 2021 Fungible. All rights reserved.
 */
#ifndef _INC_PDR_H_
#define _INC_PDR_H_

#include <stdint.h>
#include "pldm_pmc.h"
#include "utils.h"

struct numeric_sensor_pdr  thermal_sensor1 = {
        .hdr = {
            .handler = 0,
            .version = 1,
            .type = 0x2,
            .change = 0,
            .len = host2pldm_16(sizeof(struct numeric_sensor_pdr) - sizeof(struct pldm_common_pdr_hdr))
        },
        .hdl_id = 0x0000,
        .sens_id = host2pldm_16(1),
        .type = host2pldm_16(0x50),
        .inst_num = 0,
        .cid = CHIP_CONTAINER_ID,
        .init = 0,
        .has_pdr = 0,
        .base_unit = 2,
        .unit_mod = 0,
        .rate = 0,
        .base_oem = 0,
        .aux_uint = 0,
        .aux_mod = 0,
        .aux_rate = 0,
        .rel = 0,
        .aux_hdlr = 0,
        .is_linear = 1,
        .data_size = 1,
        .res = host2pldm(0x3f800000),
        .offset = 0,
        .accuracy = 0,
        .plus_tol = 0,
        .minus_tol = 0,
        .hysteresis = 0x05,
        .support_thold = PLDM_UPPER_WARNING_SUPPORT | PLDM_UPPER_CRITICAL_SUPPORT | PLDM_UPPER_FATAL_SUPPORT,
        .thold_hys = 0,
        .trans_interval = 0,
        .update_interval = host2pldm(0x3f800000),
        .max = 0x6E,
        .min = 0,
        .range = 1,
        .range_fileds_support = 0xf,
        .nominal_val = 0,
        .normal_max = UPPER_WARNING_TH,
        .normal_min = 0,
        .warn_high = UPPER_WARNING_TH,
        .warn_low = LOWER_WARNING_TH,
        .critc_high = UPPER_CRITICAL_TH,
        .critc_low = LOWER_CRITICAL_TH,
        .fatal_high = UPPER_FATAL_TH,
        .fatal_low = LOWER_FATAL_TH,
        .crc8 = -1,
};

#ifdef CONFIG_EXTERNAL_SENSOR_SUPPORT
struct numeric_sensor_pdr  thermal_sensor2 = {
        .hdr = {
            .handler = 0,
            .version = 1,
            .type = 0x2,
            .change = 0,
            .len = hton16(sizeof(struct numeric_sensor_pdr) - sizeof(struct pldm_common_pdr_hdr))
        },
        .hdl_id = 0,
        .sens_id = 2,
        .type = hton16(0x50),
        .inst_num = 0,
        .cid = hton16(CHIP_CONTAINER_ID),
        .init = 0,
        .has_pdr = 0,
        .base_unit = 2,
        .unit_mod = 0,
        .rate = 0,
        .base_oem = 0,
        .aux_uint = 0,
        .aux_mod = 0,
        .aux_rate = 0,
        .rel = 0,
        .aux_hdlr = 0,
        .is_linear = 1,
        .data_size = 1,
        .res = hton32(0x3f800000),
        .offset = 0,
        .accuracy = 0,
        .plus_tol = 0,
        .minus_tol = 0,
        .hysteresis = 0x05,
        .support_thold = PLDM_UPPER_WARNING_SUPPORT | PLDM_UPPER_CRITICAL_SUPPORT,
        .thold_hys = 0,
        .trans_interval = 0,
        .update_interval = hton32(0x3f800000),
        .max = hton32(110),
        .min = hton32(0),
        .range = 4,
        .range_fileds_support = 0xf,
        .nominal_val = 0,
        .normal_max = hton32(UPPER_WARNING_TH),
        .normal_min = 0,
        .warn_high = hton32(70),
        .warn_low = hton32(LOWER_WARNING_TH),
        .critc_high = hton32(75),
        .critc_low = hton32(LOWER_CRITICAL_TH),
        .fatal_high = hton32(110),
        .fatal_low = hton32(LOWER_FATAL_TH),
        .crc8 = -1,
};
#endif

#ifdef CONFIG_PLDM_STATE_SONSORS_SUPPORT
struct state_pdr  state_sensor1 = {
        .hdr = {
            .handler = 1,
            .version = 1,
            .type = 0x4,
            .change = hton16(0x1234),
            .len = hton16(sizeof(struct state_pdr) - sizeof(struct pldm_common_pdr_hdr))
        },
        .hdl_id = 1,
        .sens_id = 2,
        .type = hton16(0x50),
        .inst_num = 0,
        .cid = hton16(CHIP_CONTAINER_ID),
        .init = 0,
        .has_pdr = 0,
        .num_of_states = 3,
        .state = {{{0x0100, 0x02}, {0xfe, 0x03}}, {{0x0f00, 0x01}, {0x1e}}, {{0x1000, 0x01}, {0x06}}},
        .crc8 = -1,
};
#endif

#endif /* _INC_PDR_H_ */
