# Creating release bundles

In FunSDK repo fetch all prebuilt components:
```
./scripts/bob --sdkup release
./scripts/bob --deploy-up
```

Once all SDK components are in place then 2 typical types of bundles can be created - release or sdk (for funos development)

## Release bundle

The following command will appropriately patch all binaries, sign them, generate nor flash and emmc images and generate a bundle installer script (as well as manufacturing installer and a release tarball)
```
./bin/flash_tools/release.py --action all --destdir <build_folder> --chip <chip_type> --force-version <desired_build_number_in_signatures> --force-description <desired_description_in_signatures> --default-config-files
```

## SDK customer bundle

The following steps are required to create a minimal bundle for customer use for SDK development.
The main difference between a standard and customer bundles is that a customer bundle would only contain an updated FunOS build and an original (signed) funvisor image (kernel+rootfs). No other components are present, customers are not expected to sign anything other than the funos build they make themselves.
For that reason the steps are slightly more complicated to create a correct bundle:

```
./bin/flash_tools/release.py --action sdk-prepare --destdir <build_folder> --chip <chip_type> bin/flash_tools/mmc_config_sdk.json bin/flash_tools/key_bag_config.json  --force-version <build_number> --force-description "customer sdk bundle"
cd <build_folder>
./release.py --destdir . --action sign --default-config-files
```
After these steps, `build_folder` will contain a signed funvisor image, funos image and all scripts required to generate a bundle by the customer.
Customer can then generate their own bundles by taking the contents of `build_folder` and running
```
./release.py --destdir . --action sdk-release --default-config-files
```
