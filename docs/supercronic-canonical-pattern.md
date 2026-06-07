# Canonical Supercronic Dockerfile Pattern

This document records the canonical pattern for lucos scheduled-job containers, validated
as part of the spike in issue #45. Consumer migrations (lucos_arachne, lucos_dns,
lucos_media_weightings, lucos_contacts_googlesync_import) copy from this reference.

The pattern will be documented in `lucos/docs/engineering-patterns.md` when the repo is
decommissioned (#46).

---

## Validated behaviours (spike #45, 2026-06-07)

All tests run on `python:3.14.2-alpine` with supercronic v0.2.46:

| Behaviour | Result | Notes |
|---|---|---|
| **Native env propagation** | ✅ pass | Container env vars appear in job process without any `.env` dump — `printenv SYSTEM` from a cron job output `lucos_scheduled_scripts` correctly |
| **Logging** | ✅ pass | Job stdout/stderr appears in `docker logs` via supercronic's own log stream: `level=info msg=<output> channel=stdout` |
| **Non-root** | ✅ pass | Jobs run as `uid=1000(jobrunner)` — confirmed via `id` inside the container |
| **Cron expressions** | ✅ pass | Standard 5-field (`* * * * *`, `17 * * * *`) and 6-field (with seconds at end) expressions validated via `-test` flag and live firing |
| **Signals** | ✅ pass | `docker stop` (SIGTERM) causes clean shutdown in ~70ms with exit code 0; no orphaned processes; supercronic logs "waiting for jobs to finish" then "exiting" |
| **Binary sourcing — arm64** | ✅ pass | Built natively on arm64; SHA1 verified (`639ab81a72771990790df7ee87d9acfe88e5fa83`) |
| **Binary sourcing — amd64** | ✅ pass | Built via `--platform linux/amd64` on arm64 host; SHA1 verified (`5bcefed628e32adc08e32634db2d10e9230dbca0`) |

No blockers found. The ADR-0001 decision stands.

---

## Canonical Dockerfile

```dockerfile
FROM python:<version>-alpine

# Install supercronic v0.2.46 — a container-native cron runner that propagates the
# container environment to jobs natively, logs stdout/stderr to docker logs, and runs
# as a non-root user with standard crontab syntax.
# Update SUPERCRONIC_VERSION and the sha1sums for the corresponding release when upgrading.
# Latest releases: https://github.com/aptible/supercronic/releases
ARG TARGETARCH
RUN set -e; \
    case "$TARGETARCH" in \
        amd64) sha1sum="5bcefed628e32adc08e32634db2d10e9230dbca0" ;; \
        arm64) sha1sum="639ab81a72771990790df7ee87d9acfe88e5fa83" ;; \
        *) echo "Unsupported architecture: $TARGETARCH" >&2; exit 1 ;; \
    esac; \
    wget -qO /usr/local/bin/supercronic \
        "https://github.com/aptible/supercronic/releases/download/v0.2.46/supercronic-linux-${TARGETARCH}"; \
    echo "${sha1sum}  /usr/local/bin/supercronic" | sha1sum -c -; \
    chmod +x /usr/local/bin/supercronic

# Install Python dependencies directly (no base image needed)
# Each repo owns its own Pipfile or requirements.txt
RUN pip install --no-cache-dir <your-dependencies-here>
# Or, if using pipenv:
# COPY Pipfile Pipfile.lock .
# RUN pipenv install --system --deploy

# Run jobs as a non-root user
RUN adduser -D jobrunner
USER jobrunner
WORKDIR /home/jobrunner

COPY crontab /crontab
COPY <your-scripts> .

CMD ["supercronic", "/crontab"]
```

---

## Crontab file convention

Each repo has a `crontab` file in its Docker build context:

```cron
# Standard 5-field format: MIN HOUR DAY MONTH DOW
# (same as /etc/crontab — no asterisk in the SECOND position is needed)
15 04 * * * python /home/jobrunner/job.py
30 03 * * 0 python /home/jobrunner/weekly-job.py
```

**Using pipenv:**
```cron
15 04 * * * pipenv run python /home/jobrunner/job.py
```

**Crontab format notes:**
- Standard 5-field: `MIN HOUR DAY MONTH DOW`
- 6-field with seconds (optional): `MIN HOUR DAY MONTH DOW SEC` (SECOND is at the END, not the front)
- Special macros supported: `@hourly`, `@daily`, `@weekly`, `@monthly`, `@yearly`
- **`@every <duration>` is NOT supported in crontab file format** — use standard expressions instead
- Test with `supercronic -test /crontab` before deploying

---

## Supercronic pin and update story

supercronic is a static Go binary fetched from GitHub releases at image build time.
Each repo pins the version explicitly in its Dockerfile.

**Pinning:** The Dockerfile hardcodes the version (`v0.2.46`) and SHA1 checksums for
each architecture. The `sha1sum -c -` check ensures the downloaded binary matches
exactly — build fails if the binary is tampered or the URL changes.

**Updating:** When a new supercronic release is available:

1. Visit https://github.com/aptible/supercronic/releases
2. Note the new version tag (e.g. `v0.2.47`)
3. From the release notes, copy the SHA1 checksums for `supercronic-linux-amd64` and
   `supercronic-linux-arm64`
4. Update the version and both SHA1 values in the Dockerfile

There is no automated updater (no Dependabot support for binary downloads). Checking
the releases page periodically is the manual maintenance path, or watch the repo for
new releases via GitHub notifications.

---

## Key differences from the old base image pattern

| Old pattern (`lucas42/lucos_scheduled_scripts`) | New pattern (supercronic) |
|---|---|
| `FROM lucas42/lucos_scheduled_scripts:<tag>` | `FROM python:<version>-alpine` (no base image) |
| Env vars injected via `cron.sh` sed hack → `.env` file → pipenv auto-load | Env vars propagated natively by supercronic (container is `CMD`, so env is container env) |
| `crond -f -L /dev/stdout` + `syslogd` | `supercronic /crontab` — native logging, no syslogd needed |
| `RUN echo "* * * * * command" \| crontab -` | `COPY crontab /crontab` |
| Runs as root in `/root` | Runs as non-root `jobrunner` user |
| Shared libraries installed in base image (unpinned) | Each repo installs its own dependencies (pinned via Pipfile.lock / requirements.txt) |
