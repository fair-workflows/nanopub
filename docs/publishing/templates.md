# Using nanopublications templates

The nanopub library provides a few objects to easily publish specific types of nanopublications, such as claims, retraction, nanopub indexes, or ORCID introductions.

You can also easily create your own template by inheriting from the `Nanopub` class.

## 💬 Claim

Publish a simple [HYCL](http://purl.org/petapico/o/hycl) claim:

```python
from nanopub import NanopubConf, NanopubClaim

np_conf = NanopubConf(profile=load_profile(), use_test_server=True)

np = NanopubClaim(
	claim='All cats are grey',
    conf=np_conf,
)
np.publish()
```

## 🗂️ Nanopub index

To publish an index of nanopublications. Note that a nanopub cannot contain more than 1200 triples. So to publish large index with more than 1200 elements we need to split it and publish multiple nanopublications: the different nanopub index that composes this index, and a top level index that points to all the nanopub indexes.

For this we will use the `create_nanopub_index()` function instead of directly instantiating a `NanopubIndex`

```bash
from nanopub import NanopubConf
from nanopub.templates import NanopubIndex

np_conf = NanopubConf(profile=load_profile(), use_test_server=True)

np_list = create_nanopub_index(
	conf=np_conf,
    np_list=[
    	"https://purl.org/np/RAD28Nl4h_mFH92bsHUrtqoU4C6DCYy_BRTvpimjVFgJo",
    	"https://purl.org/np/RAEhbEJ1tdhPqM6gNPScX9vIY1ZtUzOz7woeJNzB3sh3E",
    ],
    title="My nanopub index",
    description="This is my nanopub index",
    creation_time="2020-09-21T00:00:00",
    creators=["https://orcid.org/0000-0000-0000-0000"],
    see_also="https://github.com/fair-workflows/nanopub",
)
for np in np_list:
	print(np)
	np.publish()
```

## 👤 ORCID introduction

To publish a nanopublication introducing a keypair for an ORCID.

```python
from nanopub import NanopubConf
from nanopub.templates import NanopubIntroduction

np_conf = NanopubConf(profile=load_profile(), use_test_server=True)

np = NanopubIntroduction(
    conf=np_conf,
    host=None,
)
np.publish()
```

## ✍️ Create your own template

You can create your own template by inheriting from the `Nanopub` class. It allows you to define classes to assist your users with publishing specific sets of triples.

Here is the `NanopubClaim` class explained:

```python
from rdflib import RDF, RDFS, Literal, URIRef

from nanopub.config import NanopubConf
from nanopub.namespaces import HYCL
from nanopub.nanopub import Nanopub

class NanopubClaim(Nanopub):

    def __init__(
        self,
        # Define the args the users should provide
        claim: str,
        conf: NanopubConf,
    ) -> None:
        # Enforce a specific nanopub conf
        conf.add_prov_generated_time = True
        conf.add_pubinfo_generated_time = True
        conf.attribute_publication_to_profile = True
        super().__init__(
            conf=config,
        )

        # Build the nanopub assertion from the args
        this_statement = self._namespace.claim
        self.assertion.add((this_statement, RDF.type, HYCL.Statement))
        self.assertion.add((this_statement, RDFS.label, Literal(claim)))

        orcid_id_uri = URIRef(self.profile.orcid_id)
        self.provenance.add((orcid_id_uri, HYCL.claims, this_statement))
```
