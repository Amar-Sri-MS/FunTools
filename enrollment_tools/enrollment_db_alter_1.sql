--
-- PostgreSQL
--
-- this is the first alteration SQL file for enrollment db: allow P384 keys as puf_key
-- this should be run after the creation script if necessary.
--

BEGIN;
ALTER TABLE enrollment DROP CONSTRAINT enrollment_puf_key_check;
ALTER TABLE enrollment ADD CONSTRAINT enrollment_puf_key_check CHECK(octet_length(puf_key) = 64 OR octet_length(puf_key) = 96);
COMMIT;
