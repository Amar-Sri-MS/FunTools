# Get your host's UID and GID
export HOST_UID=$(id -u)
export HOST_GID=$(id -g)

echo $HOST_UID
echo $HOST_GID

# Build the Docker image
sudo docker build --build-arg UID=$HOST_UID --build-arg GID=$HOST_GID -t bmcbuild .

