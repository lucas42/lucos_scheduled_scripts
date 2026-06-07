# ADR-0001: Decommission the base image in favour of a container-native cron (supercronic)

**Date:** 2026-06-07
**Status:** Accepted
**Discussion:** https://github.com/lucas42/lucos_scheduled_scripts/issues/44

## Context

`lucos_scheduled_scripts` publishes a base Docker image (`lucas42/lucos_scheduled_scripts:<tag>`) that downstream cron containers build `FROM`. It provides three things:

1. running `crond` and piping job output to the docker logs (via `syslogd`);
2. **injecting the container's environment variables into cron jobs** — because system cron deliberately strips the environment;
3. pre-installing two shared clients (`lucos_loganne_pythonclient`, `lucos_schedule_tracker_pythonclient`) via an unpinned `pip install`.

The env-injection (item 2) is the only non-trivial thing the image does, and it is a fragile hack. `cron.sh` dumps the container environment to a `.env` file through a chain of `sed` quoting tricks (to survive spaces, newlines and quotes), which is then picked up because most jobs run under `pipenv run` (pipenv auto-loads `.env`). The one consumer that runs plain `python` (`lucos_dns/sync`) instead relies on busybox `crond`'s environment passthrough. So there are two different propagation paths held together by coincidence.

Item 3 made image builds **non-reproducible** (a given tag installs whatever client versions float at build time) and the published version a weak contract — this was the original subject of issue #44. But the more fundamental observation is that **most consumers already declare these clients in their own `Pipfile`** (`lucos_arachne` ingestor, `lucos_media_weightings`, `lucos_contacts_googlesync_import`, and `lucos_dns` sync via `pyproject.toml`), so the bundle is largely redundant. Once the libraries move to the consumers, the base image is left providing only a cron-env hack.

The question #44 ultimately raised is therefore not "how do we version this base image" but "is a dedicated base image worth it at all?". System cron stripping the environment is a solved problem, and solving it does not require a bespoke image.

## Decision

1. **Standardise lucos scheduled-job containers on [supercronic](https://github.com/aptible/supercronic)** — a single static cron binary that runs each job with its own environment (and since it is the container's `CMD`, that is the container's environment), logs job output to its own stdout/stderr, runs as a non-root user, and uses standard crontab syntax. The canonical pattern is roughly:

   ```dockerfile
   FROM python:<version>-alpine
   # copy the pinned supercronic binary
   COPY crontab /crontab
   CMD ["supercronic", "/crontab"]
   ```

2. **Each scheduled-job repo owns its own dependencies** (its `Pipfile`/`pyproject.toml` declaring the clients it uses) and its own ADR-0011 real-interface test, rather than inheriting anything from a base image.

3. **Decommission `lucos_scheduled_scripts`** — stop publishing the base image and archive the repo — once all consumers have migrated.

4. **Document the supercronic pattern** in `lucos/docs/engineering-patterns.md` so future scheduled-job containers follow it without a base image.

This decision is **contingent on a validation spike** (#45) confirming supercronic behaves on `python:*-alpine` across amd64 + arm64 — native env propagation, stdout logging, non-root execution, correct cron-expression firing, and clean SIGTERM. If the spike surfaces a blocker, the decision is revisited before any consumer is migrated. (lucas42's framing was "happy to *try* supercronic", which this spike-first sequencing honours.)

## Alternatives considered

1. **Keep the base image, just version it properly** (Pipfile + lock, plus automation to make a breaking dependency bump major the image). Rejected: it builds versioning machinery around a component whose only real value is a cron-env hack that a container-native cron does better, and it does not answer the "is the base image worth it" question. (The semver-from-dependency gap it would have to solve is real and estate-wide — see #44 — but it is better solved where it matters rather than to prop up this image.)

2. **Keep the base image but swap its internals to supercronic.** Removes the env hack, but keeps a whole repo plus release pipeline that still has to be versioned and `FROM`-chained, for a marginal DRY benefit over ~3 lines per consumer.

3. **A plain entrypoint `sleep` loop with no cron.** Rejected: the jobs use real cron expressions (specific times, day-of-week), so this reinvents cron poorly.

4. **Host-level scheduling (systemd timers) or a central scheduler triggering one-shot containers.** A larger architectural change; the containers self-schedule today and that works. Recorded as the long-term option if scheduling is ever centralised.

5. **Other container cron tools (yacron, ofelia, dcron).** Viable, but supercronic is the most widely-used, boring, single-binary option with native environment propagation; none offers an advantage here.

## Consequences

### Positive

- The `.env`-dump + `sed`-quoting + pipenv-`.env` coupling and `syslogd` all disappear; jobs receive the container environment natively, by one mechanism instead of two.
- Image builds become reproducible and dependency-version ownership moves to each consumer — where ADR-0011's real-interface test already guards correctness and where the consumer knows its own usage.
- Jobs run **non-root** (today everything runs as root in `/root`).
- One fewer repo and release pipeline in the estate; the #44 versioning problem is dissolved rather than solved.

### Negative

- ~3 boilerplate lines per consumer `Dockerfile` instead of one `FROM` (the DRY cost), mitigated by documenting the canonical pattern in `engineering-patterns.md`.
- A one-time migration of four consumers plus this repo's own test container, then archival.
- supercronic is a downloaded binary (not a pip/docker dependency), so its version is pinned per repo and updated manually or via a custom updater — a small new maintenance point in each repo.
- A brief transition window where some consumers run under supercronic while others still build `FROM` the base image. Harmless — they are independent.

## Migration & follow-up

Tracked under the umbrella issue #44:

- **#45** — validation spike + canonical pattern (the gate).
- Per-consumer migrations (blocked on #45): `lucos_arachne` ingestor (lucas42/lucos_arachne#611), `lucos_dns` sync (lucas42/lucos_dns#97), `lucos_media_weightings` (lucas42/lucos_media_weightings#247, coordinate with the loganne-v2 work in lucas42/lucos_media_weightings#246), `lucos_contacts_googlesync_import` (lucas42/lucos_contacts_googlesync_import#192).
- **#46** — decommission and archive per `lucos/docs/repo-archival.md` (a base-image/build-artifact repo with no configy service, so Phase 2 service-teardown is skipped), including the `engineering-patterns.md` update.
