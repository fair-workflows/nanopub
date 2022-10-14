# Publishing with the command-line

Once installed, you can use the `nanopub` library through the `np` command line interface to sign and publish Nanopublication.

!!! info "Profile setup"

	Make sure your profile is properly set by running `np profile`

## Sign

```bash
np sign nanopub.trig
```

This will generate the signed nanopub in a file `signed.nanopub.trig`

## Publish

```bash
np publish signed.nanopub.trig
```

## Help

You can also show the help for the different commands with the `--help` flag.

```bash
np --help
```
