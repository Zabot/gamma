# Gamma Password Manager
Gamma is a simple, lightweight terminal password manager designed
with the intention of minizing user excise to maximize the chance
of it actually being used.

Account information is stored in a sqlite database (default is
`~/.passwords.db`) and encrypted with AES from pyCrypto. Comments
regarding improving security are welcomed.

# Installation

```
pip install -r requirements.txt
pip install .
```

# Usage

## Adding an account

```
gamma -c [ACCOUNT_NAME]
```

Creates a new encrypted account entry and prompts for needed information.
If `ACCOUNT_NAME` is specified on the command line, it will be automatically
filled in as the default in the prompts, otherwise the default will be empty

## Listing all accounts

```
gamma
```

Invoking gamma with no arguments will list all accounts in the database and
display an interactive prompt to select one to retreive.


## Retrieving an account

```
gamma SEARCH
```

Gamma tries to match the `SEARCH` to any of the known passwords
in the database. If multiple close matches are found, a disambiguation
dialog will be shown, and the password for the desired account
will be copied to the clipboard

## Password generation
Leaving the password field blank while creating a new account will
generate a random 32 character password and copy it to the clipboard when exiting.

