# Platform Agents

Provides client API for information about DPU

To make golang work with proprietary fungible repositories run:

```sh
$ export GOPROXY=direct
$ export GOSUMDB=off
```

Also modify ~/.gitconfig to include:

```
[url "git@github.com:"]
    insteadOf = https://github.com/
```

Then you may run `go build` and `go test`.