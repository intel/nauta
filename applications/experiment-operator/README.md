# Nauta-operator

TODO: write some general description

## Developer guide

### Preparing environment with pyenv

```bash
$ pyenv local 3.7.4
$ eval "$(pyenv init -)"
$ pip install -r requirements.txt
$ pip install -r requirements-dev.txt
```

### Running operator locally

```bash
$ kubectl apply -f run_crd.yaml
$ kopf run nauta_operator.py
```

Now you can create a Run resource using nctl, or create an example Run using kubectl:
```bash
$ kubectl apply -f example_runs/test_run.yaml
```

Note that shutting down operator may take some time, up to ~1-2 minutes.

### Running tests

Make sure that you set KUBECONFIG environment variable properly before running tests.
```bash
$ pytest .
```

### Deployment
TODO

### Development notes

* Use async functions whenever possible in order to avoid blocking operator thread
* Make sure to `await` all async functions calls (beware of `RuntimeWarning: coroutine was never awaited` in operator logs)
* In monitoring tasks (e.g. tasks with infinite loop) make sure to catch 