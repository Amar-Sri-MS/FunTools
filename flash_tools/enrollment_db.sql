--
-- PostgreSQL setup: notes
--
-- For the moment, a simple setup is used for the PostgreSQL database: current user is super user
-- and authenticated by its OS login. The enrollment script should run under a more restricted user
-- that can only QUERY and INSERT (TBD)
--
-- steps:
-- $ sudo apt-get install postgresql
-- $ sudo -u postgres createuser -s $USER
-- $ createdb enrollment_db
-- $ psql -f enrollment_db.sql -d enrollment_db
--
--
-- To interact with PostgreSQL:
-- $ psql -d enrollment_db

--
-- enrollment table: stores the whole signed certificate in order
--

CREATE TABLE IF NOT EXISTS enrollment (
 enroll_id	    SERIAL,
 magic 		    BYTEA NOT NULL CHECK (OCTET_LENGTH(magic)=4),
 flags 		    BYTEA NOT NULL CHECK (OCTET_LENGTH(flags)=4),
 serial_info 	    BYTEA NOT NULL CHECK (OCTET_LENGTH(serial_info)=8),
 serial_nr	    BYTEA NOT NULL CHECK (OCTET_LENGTH(serial_nr)=16),
 puf_key            BYTEA NOT NULL CHECK (OCTET_LENGTH(puf_key)=64),
 nonce		    BYTEA NOT NULL CHECK (OCTET_LENGTH(nonce)=48),
 activation_code    BYTEA NOT NULL CHECK (OCTET_LENGTH(activation_code)=888),
 rsa_signature	    BYTEA NOT NULL CHECK (OCTET_LENGTH(rsa_signature)=516),
 timestamp          TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
 PRIMARY KEY (serial_info, serial_nr) );
