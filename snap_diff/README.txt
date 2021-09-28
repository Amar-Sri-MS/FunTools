1. Before starting to build snap_diff tool, install prerequisites by running commands below:
    1. sudo apt update
    2. sudo apt install build-essential
    3. sudo apt-get install uuid-dev

2. Next, build the tool by running following command:
    gcc snap_diff.c -o snap_diff -luuid

3. Run snap_diff -h to get help on the tool. Some sample tool parameters:
    1. Below command generates list of blocks that changed between snapshot represented by namespace /dev/nvme4n1 and snapshot with uuid 75089902-ff97-4916-b909-4e3978b20b96 for all blocks and saves the output in diff.json. The output is saved in block format.
        snap_diff -d:/dev/nvme4n1 -t:75089902-ff97-4916-b909-4e3978b20b96 -f:diff.json
    2. Below command generates list of blocks that changed between snapshot represented by namespace /dev/nvme4n1 and snapshot with uuid 75089902-ff97-4916-b909-4e3978b20b96 for all blocks and saves the output in diff.json. The output is saved in range format.
        snap_diff -d:/dev/nvme4n1 -t:75089902-ff97-4916-b909-4e3978b20b96 -f:diff.json -r
    3. Below command generates list of blocks that changed between snapshot represented by namespace /dev/nvme4n1 and snapshot with uuid 75089902-ff97-4916-b909-4e3978b20b96 for 655360 blocks starting with block 0 and saves the output in diff.json.
        snap_diff -d:/dev/nvme4n1 -t:75089902-ff97-4916-b909-4e3978b20b96 -f:diff.json -s:0 -l:655360
