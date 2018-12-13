# Create a User Account
Creating a new user account creates a user account configuration file compliant in format with kubectl configuration files. 

## Setting Up Admin Account
Before creating Admin accounts, you need to complete the following steps:
1. Install dlsctl based on your IT requirements.
2. Copy the `dls4e-admin.config` file to the machine where dlsctl resides.
    * **Optional:** Copy the file, change the name of the file, and then modify the values within the file for the following fields. 
    
        `contexts:`
        `- context:`
            `user: new-user-name`
        `users:`
          `- name: new-user-name`

3. Set up `KUBECONFIG` variable to point to the full path of dls4e-admin.config and follow the instructions below to create users.
   * **Execute:** `export KUBECONFIG=~/.kube/dls4e-admin.config`

## Creating a User
To create a user, perform these steps:

**Note:** The following is used to create a Deep Learning Studio user, _not an Admin_. In addition, a user _does not_ have SSH access to the servers. 

1. The dlsctl user create command sets up a namespace and associated roles for the named user on the cluster. It sets up home directories, named after the username, on the input and output
network shares with file-system level access privileges.
    * **Execute:** `dlsctl user create <username>`

2. This command also creates a configuration file named .config and places this file in the user's home directory.

   * **Note 1:** Users with the same name cannot be created directly after being removed(see [Troubleshooting](Z_examples/Troubleshooting) for more details). 

   * **Note 2:** User names are limited to 32 characters maximum, must be lowercase,  no underscores, periods, or special characters, and must start with a letter not a number. You can use a hyphen to join user names, for example: john-doe. 

3. To verify that your new user has been created:
    * **Execute:** `dlsctl user list`

4. This lists all users, including the new user just added, but does not show admins. An example is shown below. 

![New Users Added](Z_examples/Examples.jpg)

5. As Admin, provide username.config file to the Intel DL Studio user. The user can save the .kube subdirectory in their home directory by doing the following:
      * **Execute:** `cp <username>.config ~/.kube/.`
6. Use the export command to set this variable for the user:
      * **Execute:** `export KUBECONFIG=~/.kube/<username>.config`
