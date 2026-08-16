# Security policy

Report vulnerabilities through a private GitHub security advisory. Do not include exploit details or secrets in public issues.

The CLI performs no network requests and uses no credentials. It parses local JSONL and produces local reports. JSON inputs can be large or malformed, so evaluate untrusted files in a resource-limited, least-privilege environment and review output destinations.

Report publication does not follow application-controlled output-directory symlinks or pre-existing report/JSONL symlinks. Every artifact is staged before commit, and a commit failure restores the complete previous set or leaves a previously empty destination empty. Cooperating writers serialize publication with an exclusive advisory lock on the verified output directory; unsupported or failed locking fails closed. The lock protects only cooperating processes on filesystems that honor `flock`-style advisory locks, so it does not serialize unrelated writers or filesystems that ignore those locks. Target identities are rechecked immediately before publication, and ambiguous rename outcomes are reconciled before rollback. Descriptor-relative and compatibility-fallback publication both close acquired temporary descriptors if text-stream setup fails. Invalid output paths produce CLI status `2`. User-selected task and answer paths are read as ordinary local files, so explicitly supplied input symlinks are followed; apply normal filesystem trust and permission controls to benchmark inputs.

Only the latest release is supported.
