# Deleting a User Account

Only an Administrator can delete user accounts and deleting a user removes that user's account from the Nauta software; therefore, that user _will not_ be able to log in to the system. This will halt and remove all experiments and pods; however, all artifacts related to that user's account, such as the users input and output folders and all data related to past experiments they have submitted remain. To create a User Account, refer to [Creating a User Account](../actions/create_user.md). 

This section discusses the following main topics:

- [Removing a User](#removing-a-user)

- [Using the purge Command](#using-the-purge-command)

## Removing a User

Execute the following command to remove a user:

  `nctl user delete <username>`

Respond to this question to confirm the previous step. 

`Do you want to continue? [y/N]: Press y to confirm deletion.`

### Limitations	

The command may take up to 30 seconds to delete the user. You may receive the message: _User is still being deleted_. Check the status of the user after a few minutes. Recheck as desired.

## Using the purge Command

Use this commmand to permanently remove (_Purge_) all artifacts associated with the user, including all data related to past experiments submitted by that user (but excluding the contents of the user’s input and output folders):

### Purging Process

Execute the following command to purge a user: 

  `nctl user delete <username>  --purge`
  
Respond to this question to confirm the previous step. 

`Do you want to continue? [y/N]: Press y to confirm deletion.`

### Limitations	

The Nauta `user delete` command may take up a few minutes to delete the user. A new user with the same user name _cannot_ be created until after the delete command confirms that the first user with the same name has been deleted. 

----------------------

## Return to Start of Document

* [README](../README.md)

----------------------

