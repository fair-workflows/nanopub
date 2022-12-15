# Use the command line interface

Once installed, you can use the `nanopub` library through the `np` command line interface to sign and publish Nanopublication.

## 👤 Check the current user profile

```bash
np profile
```

## ✍️ Set your user profile

See the [setup instructions](/nanopub/getting-started/setup) page for more details about setting up your profile.

```bash
np setup
```

## ✒️ Sign nanopubs

Sign a nanopublication from a file, this will generate the signed nanopub in a new file `signed.nanopub.trig` alongside the original:

```bash
np sign nanopub.trig
```

## 📬️ Publish nanopubs

Publish a nanopublication from a signed file:

```bash
np publish signed.nanopub.trig
```

Or directly publish a nanopublication from an unsigned file:

```bash
np publish nanopub.trig
```

You can also publish to the test server:

```bash
np publish nanopub.trig --test
```

## ☑️ Check signed nanopubs

Check if a signed nanopublication is valid:

```bash
np check signed.nanopub.trig
```

## ℹ️ Get help

Display the help for the different commands with the `--help` flag.

```bash
np --help
np sign --help
```
