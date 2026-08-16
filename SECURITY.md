# Security policy

Report vulnerabilities through a private GitHub security advisory. Do not include exploit details or secrets in public issues.

The CLI performs no network requests and uses no credentials. It parses local JSONL and produces local reports. JSON inputs can be large or malformed, so evaluate untrusted files in a resource-limited, least-privilege environment and review output destinations.

Only the latest release is supported.
