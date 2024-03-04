# Run the Docker container
sudo docker run --rm --name bmcbuild0 \
    -v ${BUILD_SOURCESDIRECTORY}:/home/bmcbuild/src \
    -v ${BUILD_STAGINGDIRECTORY}:/home/bmcbuild/artifacts \
    bmcbuild \
    build-i2c-dbg.sh

