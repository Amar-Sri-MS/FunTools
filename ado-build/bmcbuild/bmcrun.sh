# Run the Docker container
sudo docker run -it --rm --name bmcbuild0 -v ${BUILD_SOURCESDIRECTORY}:/home/bmcbuild/src bmcbuild uname -a

