# Deleting a User Account

Only an administrator can delete a user. 

Deleting a user removes that user's account from the Nauta software; that user will not be able to log in to the system. 
This will halt and remove all experiments and pods, however all artifacts related to that user's account, such as the users input 
and output folders and all data related to past experiments he/she submitted will remain.

  `$ nctl user delete <user_name>`

To permanently remove (purge) all artifacts associated with the user, including all data related to past experiments submitted by 
that user (but excluding the contents of the user’s input and output folders):

  `$ nctl user delete <user_name> -p`

Both commands above will ask for confirmation. Enter Y or Yes to delete the user.

**Note**: The command may take up to 30 seconds to delete the user. A new user with the same user name cannot be created until after the delete command confirms that the first user with the same name has been deleted. 
 
