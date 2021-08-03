

all: signing_server.run

signing_server.run: build/signing_server.tar.gz
	cp install_signing_server.sh build
	makeself build $@ "Fungible Simple Signing Server Installer" ./install_signing_server.sh

build/signing_server.tar.gz: build/signing_server.tar
	gzip -f $^

# create a flat archive with the script and the key files
build/signing_server.tar: | build
	tar --owner=root --group=root -cf $@ signing_server.cgi
	tar --owner=root --group=root -uf $@ -C ../development_keys_certs `find ../development_keys_certs -name '*.pem' -exec basename {} \;`


build:
	mkdir -p $@

clean:
	rm -rf build
	rm -f signing_server.run
