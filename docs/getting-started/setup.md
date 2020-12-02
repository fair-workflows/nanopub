# Setup instructions

## Install nanopub library
Install using pip:
```
pip install nanopub
```

## Setup your profile

To publish to the nanopub server you need to setup your profile (note that you can use
fetch and search functionality without a profile). This allows the nanopub server to identify you.

Run the following interactive command:
```
setup_profile
```
This will setup the following:

### Stored profile
A local version of the profile will be stored in the
nanopub user config dir (by default `HOMEDIR/.nanopub/profile.yml`)

### RSA keys
It will add and store RSA keys to sign your nanopublications. By
default they are stored under `HOMEDIR/.nanopub/id_rsa` and `HOMEDIR/.nanopub/id_rsa.pub`.

### ORCID iD
This includes your [ORCID iD](https://orcid.org/) (i.e. https://orcid.org/0000-0000-0000-0000).
If you don't have an ORCID iD yet, you need to [register](https://orcid.org/register). We use
the ORCID iD to automatically add as author to the provenance of any nanopublication you will publish
using this library.

### Introductory nanopublication
We encourage you to make use of `setup_profile`'s option 
to publish your profile to the nanopub servers. This links your ORCID iD
to your RSA key, thereby making all your publications linkable to you.
Here is an [example introductory nanopublicaiton](http://purl.org/np/RAy1CYBfBYFd_TFI8Z_jr3taf6fB9u-grqsKyLzTmMvQI).

The link to this nanopublication is also stored in your profile.

## Dependencies
The ```nanopub``` library currently uses the [nanopub-java](https://github.com/Nanopublication/nanopub-java)
tool for signing and publishing new nanopublications. This is automatically installed by the library.
