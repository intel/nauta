# Creating a User Account

The user is the _Data Scientist_ who performs deep learning experiments to train models that will, after training and testing, be deployed in the field. Creating a new user account creates a user account configuration file compliant in format with `kubectl` configuration files. Refer to [Deleting a User Account](../actions/delete_user.md) to delete a User Account. 

This section discusses the following main topics:

- [Experiments and User Access](#experiments-and-user-access)
- [User Name Limitations](#user-name-limitations)
- [Create the User](#create-the-user)


## Experiments and User Access 

The user has full control (`list/read/create/terminate`) over their own experiments, as well as read access (`list/read`) to experiments belonging to other users on this cluster. 

**Note:** Only an Administrator can create a user account. 

## User Name Limitations

Users with the same name _cannot_ be created directly after being removed. This is due to a user's related Kubernetes objects that are deleted asynchronously by Kubernetes and this can take some time. Consider waiting 10 minutes before creating a user with the same name.

In addition, user names are limited to a 32-character maximum and there are no special characters except for hyphens. However, all names _must_ start with a letter. You can use a hyphen to join user names, for example: john-doe.

### Create the User

Execute the following steps to create a user:

1. The `nctl user create <username>` command sets up a namespace and associated roles for the named user on the cluster. Furtermore, this command sets up home directories named after the username, on the input and output network shares with the file-system level access privileges. Create the user:
 
    `nctl user create <username>`

2. The command above also creates a configuration file named `<username>.config` that the Admin provides to the user. The user then copies that file into a local folder. 
  
3. Use the export command to set this variable for the user:
 
    `export KUBECONFIG=/<local_user_folder>/<username>.config`

4. Verify that the new user has been created with the following command:

   `nctl user list`

The command  lists all users, including the new user just added. An example is shown below (scroll right to see full contents).

```
| Name    | Creation date          | Date of last submitted job   |   Number of running jobs |   Number of queued jobs|
|---------+------------------------+------------------------------+--------------------------+-------------------------
| user1   | 2019-03-12 08:30:45 PM | 2019-02-27 07:55:13 PM       |                        1 |                       1|
| user2   | 2019-03-12 09:50:50 PM |                              |                        0 |                       0|
| user3   | 2019-03-12 09:51:31 PM |                              |                        0 |                       0|

```

----------------------
## Return to Start of Document

* [README](../README.md)

----------------------

