# FunOS DPC fuzzer

## Setup

```sh
npm install && tsc
```

## Run

```sh
node ./build/dpcfuzz.js <verb-to-fuzz>
```

## Compile binary

```sh
./node_modules/nexe/index.js ./build/dpcfuzz.js
```

## Publish binary

```sh
gzip dpcfuzz
cp dpcfuzz.gz /project/users/doc/dpcfuzz/
```