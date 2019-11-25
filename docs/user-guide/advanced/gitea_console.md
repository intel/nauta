# Gitea* Console Access

Although Nauta's underlying git system should be self-maintainable, there may be some rare cases
when manual action is required (e.g. triggering garbage collection manually, updating SSH keys).
 In order to perform these actions, or to monitor Gitea* state, Nauta administrators are able to
access Gitea's UI with admin rights using the procedure described below.

## Accessing Gitea console

- Get gitea admin credentials:
```bash
# export KUBECONFIG=<path to your admin's KUBECONFIG file>
$ kubectl get secret -n nauta -o jsonpath={.data.name} nauta-gitea-admin-secret | base64 --decode
nauta-admin
$ kubectl get secret -n nauta -o jsonpath={.data.password} nauta-gitea-admin-secret | base64 --decode
vZ25ZDDXCN
```
- Launch tunnel to Gitea's UI:
```bash
kubectl port-forward -n nauta services/nauta-gitea-http 3000:3000
```
- Open your web browser and navigate to `http://localhost:3000`
- Now you should see Gitea UI login screen, click `Sign In` button on the top bar
and enter username and password obtained in the first step
- Now you should see Gitea's dashboard, administration utilities are available at 
`Profile and settings (dropdown menu, top right of the screen) > Site administration`

## Example situation when running administration tasks manually is useful:
- Nauta users are experiencing issues with experiments' uploads, with following error message in `nctl` logs:
```
Permission denied (publickey).
fatal: Could not read from remote repository.
```
- Nauta administrator gets access to Gitea console, by following the procedure described above
- Nauta administrator runs `Rewrite '.ssh/authorized_keys' file (for Gitea SSH keys)` on the Gitea admin panel
- If `authorized_keys` were the issue, problem should be mitigated

