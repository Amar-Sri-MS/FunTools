


-- split existing data (enrollment) into the new tables
INSERT INTO fungible_dpus (serial_info, serial_nr) SELECT serial_info, serial_nr from enrollment;

INSERT INTO enrollment_certs (chip_id, magic, flags, puf_key, nonce, activation_code, rsa_signature, timestamp)
       SELECT f.chip_id, e.magic, e.flags, e.puf_key, e.nonce, e.activation_code, e.rsa_signature, e.timestamp
       FROM fungible_dpus f, enrollment e WHERE f.serial_info = e.serial_info AND f.serial_nr = e.serial_nr;
