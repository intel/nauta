# Gitea Console Access

Although Nauta's underlying Git system should be self-maintainable, there may be some rare case when manual action is required (for example, triggering garbage collection manually, updating SSH keys). To perform these actions, or to monitor Gitea state, Nauta administrators are able to access Gitea's UI with admin rights using the procedure described below.

## Accessing Gitea Console

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
1. Open your web browser and navigate to: `http://localhost:3000`
   You should see Gitea UI login screen.
   
2. Click the `Sign In` button on the top bar.

3. Enter your username and password obtained in step
   You should see Gitea's dashboard, administration utilities are available at:
   
`Profile and settings (dropdown menu, top right of the screen) > Site administration`

## Example Situation When Running Administration Tasks Manually is Useful

1. Nauta users are experiencing issues with experiments' uploads, with following error message in `nctl` logs:

   ```
   Permission denied (publickey).
   fatal: Could not read from remote repository.
   ```
2. Nauta administrator gets access to Gitea console, by following the procedure described above.

3. Nauta administrator runs `Rewrite '.ssh/authorized_keys' file (for Gitea SSH keys)` on the Gitea admin panel.

4. If `authorized_keys` were the issue, the problem should be mitigated.
