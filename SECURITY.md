# Security policy

This is research software and must not control safety-critical electrochemical hardware. Report a
potential dependency or code-execution vulnerability privately to the repository owner. Do not
include credentials, private telemetry, proprietary stack data, or licensed raw files in reports.

Only the configured University of Alberta HTTPS source is downloaded. The pipeline verifies a
fixed SHA-256 digest and rejects archive path traversal before extraction.
