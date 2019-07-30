sudo apt-get install python3-pip apache2 postgresql softhsm2
sudo pip3 install cryptography psycopg2-binary python-pkcs11

#OpenSSL latest:

wget https://www.openssl.org/source/openssl-1.1.1b.tar.gz
tar xzvf openssl-1.1.1b.tar.gz
pushd openssl-1.1.1b
./config
make
sudo make install
popd
sudo ldconfig
# try '$ openssl version'

# softhsm setup
sudo usermod -a -G softhsm www-data
sudo mkdir /var/lib/softhsm/tokens
sudo chmod g+w /var/lib/softhsm/tokens
sudo -u www-data softhsm2-util --init-token --free --label fungible_token

#store hsm pins in a file for use by script
sudo -- sh -c "echo 'fungible_token' > /etc/hsm_password"
sudo -- sh -c "echo <pin> >> /etc/hsm_password"
sudo -- sh -c "echo <so_pin> >> /etc/hsm_password"
# protect this file better -- should not be readable by all
sudo chown www-data /etc/hsm_password
sudo chmod og-r /etc/hsm_password

# import the key fpk4 by destroying the tokens directory and replace it with the one checked in
sudo rm -rf /var/lib/softhsm/tokens
sudo -u  www-data tar xzvf tokens_fpk4.tgz -C /var/lib/softhsm

# **optional for signing server**: import the development keys
sudo -u www-data python3 enrollment_hsm.py import -k fpk2 -i development_fpk2.pem --token fungible_token
sudo -u www-data python3 enrollment_hsm.py import -k fpk3 -i development_fpk3.pem --token fungible_token
sudo -u www-data python3 enrollment_hsm.py import -k fpk5 -i development_fpk5.pem --token fungible_token
# customer key
sudo -u www-data python3 enrollment_hsm.py import -k cpk1 -i cpk1.pem --token fungible_token
sudo -u www-data python3 enrollment_hsm.py import -k cpk2 -i cpk2.pem --token fungible_token


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

#enable the registration (main) site
sudo a2ensite registration.conf

# **optional for signing server**: enable the signing site (port 4443)
sudo a2ensite signing.conf
