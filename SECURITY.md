# Security

## Philosophy

repo-memory-mcp is local-first. It stores only information explicitly submitted to its tools and does not call external services.

## Threat model

The primary risks are accidental storage of credentials, accidental cross-repository mixing, and committing the local database. The implementation uses repository identifiers, parameterized SQLite queries, secret detection, and ignore rules to reduce these risks.

## Local-data considerations

The `.repo-memory/` directory contains private project memory and should remain local. Protect the filesystem and backups that contain it.

## Secret handling

Likely API keys, bearer tokens, passwords, cloud credentials, and private keys are rejected by default. Do not submit credentials to memory tools.

## Responsible disclosure

Please open a private security advisory on the GitHub repository when one is available. Until then, avoid posting exploitable details in a public issue; use the repository owner's GitHub contact or security advisory workflow.
