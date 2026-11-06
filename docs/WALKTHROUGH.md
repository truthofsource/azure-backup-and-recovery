# Follow the implemented recovery path

1. `versions` constrains the key and continuation host/path, inventories enabled flags and bounds pages/version count.
2. `Lease` acquires a finite Blob lease and checks renewal ownership before accepted writes. An overlap conflict is not the same as an arbitrary storage failure.
3. `backup` compares version coverage and age; current coverage verifies retained bytes rather than trusting the latest pointer blindly.
4. A new protected backup is kept in memory, checked for a rotation race, created under a unique name and read back. A create-only receipt precedes the latest pointer.
5. `restore_target` requires an exact owned target naming/resource/location/tag/private-RBAC boundary. `restore` checks the receipt and hash, refuses an existing key and reconciles an uncertain response.
6. Restored version coverage must match. Enabled versions receive synthetic wrap/unwrap checks; disabled versions are explicitly partial rather than silently called accepted.
7. Restore receipts leave cleanup pending. A successful cryptographic check is not evidence that the temporary vault/grants were removed.

The public transport is fictional and its wrap/unwrap fixture is not real encryption. Actual source logic and original negative tests remain inspectable in [reference](../reference/). The local database exercise is separate.
