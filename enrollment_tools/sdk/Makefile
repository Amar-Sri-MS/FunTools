
all: signing_server.tar.gz


signing_server.tar.gz: signing_server.tar
	gzip -f $^

# create a flat archive with the script and the key files
signing_server.tar:
	tar --owner=root --group=root -cf $@ signing_server.cgi
	tar --owner=root --group=root -uf $@ -C ../development_keys_certs `find ../development_keys_certs -name '*.pem' -exec basename {} \;`

clean:
	rm -f signing_server.tar*
