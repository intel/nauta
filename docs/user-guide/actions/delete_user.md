# Deleting a User Account

Only an administrator can delete a user. 

Deleting a user removes that user's account from the Nauta software; therefore, that user will not be able to log in to the system. This will halt and remove all experiments and pods; however, all artifacts related to that user's account, such as the users input and output folders and all data related to past experiments they have submitted remain.

To remove a user:

  `$ nctl user delete <user_name>`

This command asks for confirmation. 

**Do you want to continue? [y/N]:** press y to confirm deletion.

### Limitations	

The command may take up to 30 seconds to delete the user and you may receive the message: _User is still being deleted_. Check the status of the user in a while. Recheck, as desired.

## Using purge Command

To permanently remove (purge) all artifacts associated with the user, including all data related to past experiments submitted by that user (but excluding the contents of the user’s input and output folders):

  `$ nctl user delete <user_name> -p`
  
This command asks for confirmation. 

**Do you want to continue? [y/N]:** press y to confirm deletion.

### Limitations	

The Nauta `user delete` command may take up to 30 seconds to delete the user. A new user with the same username _cannot_ be created until after the delete command confirms that the first user with the same name has been deleted. 
 
 
 
 
