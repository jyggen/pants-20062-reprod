
Not Working:

```
pants --no-pantsd --no-local-cache lint ::
```

Working:

```
pants --no-pantsd --no-local-cache --process-execution-local-parallelism=1 lint ::
```