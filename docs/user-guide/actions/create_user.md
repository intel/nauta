# Creating a User Account

Only an administrator can create a user account. 

The user is the data scientist who wants to perform deep learning experiments to train models that 
will, after training and testing, be deployed in the field. The user has full control (list/read/create/terminate) 
over his/her own experiments and has read access (list/read) of experiments belonging to other users on this cluster. 
Creating a new user account creates a user account configuration file compliant in format with kubectl configuration files.

**Note 1**: A user with the same name cannot be created immediately after its’ removal. The reason is that the user's related Kubernetes objects are deleted asynchronously by Kubernetes and this can take some time. Consider waiting perhaps thirty minutes before creating a user with the same name as the user just deleted.

**Note 2**: User names are limited to 32 characters maximum, must be lowercase, no underscores, periods, or special characters, and must start with a letter not a number. You can use a hyphen to join user names, for example: john-doe.

To create a user, perform these steps:

1. The `dlsctl user create <username>`  command sets up a namespace and associated roles for the named user on the cluster. It sets up "home" directories, named after the username, on the "input" and "output" network shares with file-system level access privileges.
  * **Execute** `dlsctl user create <username>`

2. The above command also creates a configuration file named `<username>.config` and places this file in the user's home directory. As Admin, copy that file into the folder named .kube in the user's home directory:
  * **Execute**: `cp <username>.config ~/.kube/.`

3. Use the export command to set this variable for the user:
  * **Execute**: `export KUBECONFIG=~/.kube/<username>.config`

4. To verify that your new user has been created:
 * **Execute**: `dlsctl user list`

The above command lists all users, including the new user just added.
