sudo apt-get install emacs mate-terminal python3-pip apache2 postgresql softhsm2
sudo pip3 install cryptography psycopg2-binary python-pkcs11

#OpenSSL latest:

wget https://www.openssl.org/source/openssl-1.1.1b.tar.gz
tar xzvf openssl-1.1.1b.tar.gz
pushd openssl-1.1.1b
./configure
make
sudo make install
popd
# might have to reboot to update the path
# try '$ openssl version'

# softhsm setup
sudo usermod -a -G softhsm www-data
sudo mkdir /var/lib/softhsm/tokens
chmod g+w /var/lib/softhsm/tokens
sudo -u www-data softhsm2-util --init-token --free --label fungible_token --so-pin <> --pin <>

#store hsm pins in a file for use by script
sudo -- sh -c "echo 'fungible_token' > /etc/hsm_password"
sudo -- sh -c "echo <pin> >> /etc/hsm_password"
sudo -- sh -c "echo <so_pin> >> /etc/hsm_password"
# protect this file better -- should not be readable by all
sudo chown www-data /etc/hsm_password
sudo chmod og-r /etc/hsm_password

# create the key fpk4: use pin password
sudo -u www-data python3 enrollment_hsm.py create -k fpk4 --token fungible_token

#postgresql setup
sudo apt-get install postgresql
sudo -u postgres createuser -s $USER
createdb enrollment_db
psql -f enrollment_db.sql -d enrollment_db

#apache setup
#disable other site -- verify with a2query -s
sudo a2dissite 000-default.conf

#enable modules we use: ssl, cgid
sudo a2enmod ssl
sudo a2enmod cgid
sudo tar xzvf install.tgz -C /
#verify permission of installed files
sudo a2ensite registration.conf
