# GitHub Actions workflows

Active workflow files belong in this directory.

Legacy workflows were archived under `.github/workflows-legacy` so GitHub does
not execute them while the CI/CD pipeline is rebuilt from scratch.

## Active Workflows

### `build-and-push-images.yml`

Builds and pushes the four DevBoard application images to Docker Hub:

- `sunmingtao/devboard-backend`
- `sunmingtao/devboard-frontend`
- `sunmingtao/devboard-event-service`
- `sunmingtao/devboard-event-frontend`

The workflow runs on `main` when any app or workflow file changes. It can also
be started manually with `workflow_dispatch`.

Required repository secrets:

- `DOCKERHUB_USERNAME`
- `DOCKERHUB_TOKEN`

Image tags default to the short commit SHA. Manual runs can override the tag and
can optionally publish `latest` for recovery/testing, but normal dev/prod
promotion should use immutable tags.
