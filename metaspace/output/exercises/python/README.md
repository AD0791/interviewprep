# The Python path

Four counterparts to the TypeScript ladder, for [article 12](../../articles/12_python_path_fastapi_web3py.md).
They exist so that "how would you do this in Python?" is a file you can open rather than a
claim you make.

```bash
python -m venv .venv
./.venv/bin/pip install "web3>=8" fastapi httpx
./.venv/bin/python 02_read_the_chain.py     # a live read of Polygon Amoy
./.venv/bin/python 04_sign_and_recover.py   # signing, recovery, EIP-712 (offline)
./.venv/bin/python 07_indexer.py            # checkpointed, crash-safe indexer
./.venv/bin/python 10_voucher_fastapi.py    # the voucher service, with a self-test
```

Verified on 19 September 2026 against **web3.py 8.0.0** and **eth-account 0.14.0**.

Two things these files exist to show. The first is in the opening lines of
`02_read_the_chain.py`: without `ExtraDataToPOAMiddleware`, web3.py **cannot read a Polygon
block at all** — it raises `ExtraDataLengthError`, because Polygon's `extraData` field is longer
than the Ethereum mainnet rule allows. viem needs no equivalent step.

The second is the payoff in `04_sign_and_recover.py` and `10_voucher_fastapi.py`: the EIP-712
type hash comes out as `0xc97be41af9816514648878b03f762e694f0de1ef1c55a9f7cd5a230e9166f849` in
Python, in viem, and in the constant the Solidity compiler embedded in the contract. The contract
cannot tell what language signed its voucher, because interoperability lives at the protocol
rather than in any library.
