# Handle users profile

## Check your profile

You can check the profile currently used by default by running this command in your terminal:

```bash
np profile
```

## Load from files

### Load a profile.yml file

The easiest way to load a nanopub profile is to use the `load_profile()` helper function to load your user profile stored in `$HOME/.nanopub/profile.yml`:

```bash
from nanopub import load_profile

# Load from your home folder by default
p1 = load_profile()

# Or you can provide a specific path
p2 = load_profile(Path('/path/to/profile.yml'))
```

### Provide the keys filepaths

If you need to switch between multiple keys it can be convenient to be able to define the profile directly in your code, you can do so with the `Profile` class:

```bash
from pathlib import Path
from nanopub import Profile

p1 = Profile(
    name='Your Name',
    orcid_id='https://orcid.org/0000-0000-0000-0000',
    private_key=Path.home() / "id_rsa",
    public_key=Path.home() / "id_rsa.pub"
)
```

## Provide the keys as strings

If you need to switch between multiple keys you can also provide the private and public keys as string, without needing to store them in files:

```python
from nanopub import Profile

p = Profile(
    name='Your Name',
    orcid_id='https://orcid.org/0000-0000-0000-0000',
    private_key="YOUR_PRIVATE_KEY",
    public_key="YOUR_PUBLIC_KEY"
)
```
