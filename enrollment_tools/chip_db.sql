--
-- PostgreSQL setup: notes
--
-- For the moment, a simple setup is used for the PostgreSQL database:
-- super user authenticated by its OS login.
--
--
-- steps:
-- $ sudo apt-get install postgresql
-- $ sudo -u postgres createuser -s dpu_reg
-- $ sudo -u dpu_reg createdb enrollment_db
-- $ psql -f chip_db.sql -d enrollment_db
--
--
-- To interact with PostgreSQL:
-- $ psql -d enrollment_db



--
-- chip table:
--
CREATE TABLE IF NOT EXISTS fungible_dpus (
       chip_id	    	  SERIAL UNIQUE,
       serial_info	  BYTEA NOT NULL CHECK (OCTET_LENGTH(serial_info)=8),
       serial_nr	  BYTEA NOT NULL CHECK (OCTET_LENGTH(serial_nr)=16),
PRIMARY KEY (serial_info, serial_nr) );


--
-- enrollment table:
--


CREATE TABLE IF NOT EXISTS enrollment_certs (
 chip_id            INTEGER PRIMARY KEY references fungible_dpus(chip_id) ON DELETE CASCADE,
 magic 		    BYTEA NOT NULL CHECK (OCTET_LENGTH(magic)=4),
 flags 		    BYTEA NOT NULL CHECK (OCTET_LENGTH(flags)=4),
 puf_key            BYTEA NOT NULL CHECK (OCTET_LENGTH(puf_key)=64 OR OCTET_LENGTH(puf_key)=96),
 nonce		    BYTEA NOT NULL CHECK (OCTET_LENGTH(nonce)=48),
 activation_code    BYTEA NOT NULL CHECK (OCTET_LENGTH(activation_code)=888),
 rsa_signature	    BYTEA NOT NULL CHECK (OCTET_LENGTH(rsa_signature)=516),
 timestamp          TIMESTAMP DEFAULT CURRENT_TIMESTAMP);


--
-- debug table:
--

CREATE TABLE IF NOT EXISTS debug_certs (
 chip_id            INTEGER PRIMARY KEY references fungible_dpus(chip_id) ON DELETE CASCADE,
 magic              BYTEA NOT NULL CHECK (OCTET_LENGTH(magic)=4),
 debug_locks        BYTEA NOT NULL CHECK (OCTET_LENGTH(debug_locks)=4),
 auth               BYTEA NOT NULL CHECK (OCTET_LENGTH(auth)=1),
 key_index          BYTEA NOT NULL CHECK (OCTET_LENGTH(key_index)=1),
 reserved	    BYTEA NOT NULL CHECK (OCTET_LENGTH(reserved)=2),
 tamper_locks	    BYTEA NOT NULL CHECK (OCTET_LENGTH(tamper_locks)=4),
 serial_info_mask   BYTEA NOT NULL CHECK (OCTET_LENGTH(serial_info_mask)=8),
 serial_nr_mask	    BYTEA NOT NULL CHECK (OCTET_LENGTH(serial_nr_mask)=16),
 modulus            BYTEA NOT NULL CHECK (OCTET_LENGTH(modulus)=516),
 rsa_signature	    BYTEA NOT NULL CHECK (OCTET_LENGTH(rsa_signature)=516),
 pub_key_pem        VARCHAR NOT NULL,
 timestamp          TIMESTAMP DEFAULT CURRENT_TIMESTAMP);


CREATE OR REPLACE VIEW enrollment_certs_v AS
SELECT e.chip_id as chip_id,
       e.magic AS magic,
       e.flags AS flags,
       f.serial_info AS serial_info,
       f.serial_nr AS serial_nr,
       e.puf_key AS puf_key,
       e.nonce AS nonce,
       e.activation_code AS activation_code,
       e.rsa_signature as rsa_signature,
       e.timestamp as timestamp
FROM enrollment_certs e, fungible_dpus f
WHERE e.chip_id = f.chip_id;


CREATE OR REPLACE VIEW debug_certs_v AS
SELECT 	d.chip_id as chip_id,
	d.magic AS magic,
	d.debug_locks AS debug_locks,
	d.auth AS auth,
	d.key_index AS key_index,
	d.reserved AS reserved,
	d.tamper_locks AS tamper_locks,
	f.serial_info AS serial_info,
	f.serial_nr AS serial_nr,
	d.serial_info_mask AS serial_info_mask,
	d.serial_nr_mask AS serial_nr_mask,
	d.modulus AS modulus,
	d.rsa_signature AS rsa_signature,
	d.pub_key_pem as pub_key_pem,
	d.timestamp as timestamp
FROM debug_certs d, fungible_dpus f
WHERE d.chip_id = f.chip_id;


-- https://stackoverflow.com/a/15950324/4381304
CREATE OR REPLACE FUNCTION register_dpu(_serial_info bytea, _serial_nr bytea, OUT _chip_id int)
  LANGUAGE plpgsql AS
$func$
BEGIN
   LOOP
      SELECT chip_id
      FROM   fungible_dpus
      WHERE  serial_info = _serial_info AND serial_nr = _serial_nr
      INTO   _chip_id;

      EXIT WHEN FOUND;

      INSERT INTO fungible_dpus AS f (serial_info, serial_nr)
      VALUES (_serial_info, _serial_nr)
      ON CONFLICT DO NOTHING
      RETURNING f.chip_id
      INTO   _chip_id;

      EXIT WHEN FOUND;
   END LOOP;
END
$func$;


CREATE EXTENSION plpython3u;

CREATE OR REPLACE FUNCTION esrp_sign(_tbs bytea, _cert text)
  RETURNS bytea
AS $$

import requests
import hashlib

def pack_bytes_with_len_prefix(b, size):
    ''' used to transform signature/modulus to proper format '''
    len_b = len(b)
    ret = len_b.to_bytes(4, byteorder='little') + b # LE length prefix
    len_pad = size - (4 + len_b)
    if len_pad > 0:
        ret += b'\x00' * len_pad
    return ret

digest = hashlib.sha512(_tbs).digest()

url_str = "https://127.0.0.1:4443/cgi-bin/signing_server.cgi"

multi_form_data = { 'digest' : ('sha512',
                                digest,
                                'application/octet-stream',
                                {"Content-Length" : str(len(digest)) }
                                )
                   }

params = {'key' : 'fpk4'}

response = requests.post(url_str,
			 cert=_cert,
			 files=multi_form_data,
			 params=params,
			 verify=False)

raw_sig = response.content
signature = pack_bytes_with_len_prefix(raw_sig, 516)
return signature

$$ LANGUAGE plpython3u;




CREATE OR REPLACE FUNCTION resign_all_cert(_cert text) RETURNS void
LANGUAGE plpgsql AS
$func$
BEGIN

update enrollment_certs as ec
set rsa_signature = esrp_sign( v.magic||v.flags||v.serial_info||v.serial_nr||
		    	       v.puf_key||v.nonce||v.activation_code,
			       _cert)
from
	enrollment_certs_v v
where
	ec.chip_id = v.chip_id;
END
$func$;


GRANT CONNECT ON DATABASE enrollment_db to "apache";
GRANT SELECT,INSERT ON TABLE fungible_dpus, enrollment_certs, debug_certs to "apache";
GRANT SELECT ON TABLE enrollment_certs_v, debug_certs_v to "apache";
GRANT SELECT,UPDATE ON SEQUENCE fungible_dpus_chip_id_seq TO "apache";
GRANT EXECUTE ON FUNCTION  register_dpu(_serial_info bytea, _serial_nr bytea, OUT _chip_id int) TO "apache";
