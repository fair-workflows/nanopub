# Publishing with the command-line

Once installed, you can use the `nanopub` library through the `np` command line interface to sign and publish Nanopublication.

!!! info "Prerequisite for publishing"

	Before you can sign and publish you should [setup your profile](/nanopub/getting-started/setup), check if it is properly set by running `np profile` in your terminal.

## Sign

```bash
np sign nanopub.trig
```

This will generate the signed nanopub in a file `signed.nanopub.trig`

## Publish

```bash
np publish signed.nanopub.trig
```

## Check

Check if a signed nanopublication is valid:

```bash
np check signed.nanopub.trig
```

## Help

You can also show the help for the different commands with the `--help` flag.

```bash
np --help
```
