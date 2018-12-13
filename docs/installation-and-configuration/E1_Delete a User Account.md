# Delete a User Account
Only an Administrator can delete user accounts and deleting a user removes that user's account from the Intel DL Studio software; therefore, that user _will not_ be able to log in to the system. This will halt and remove all experiments and pods, however all artifacts related to that user's account, such as the users input and output folders and all data related to past experiments he/she submitted remains. 

To remove a user:

*	**Execute:** `dlsctl user delete <user_name>`

This command asks for confirmation. 

   *	**Do you want to continue? [y/N]:** press y to confirm deletion.

**Note:** The command may take up to 30 seconds to delete the user and you may receive the message: User is still being deleted. Please check the status of the user in a while. Please check the status of the user in a while. Recheck, if desired.

To permanently remove (purge) all artifacts associated with the user and all data related to past experiments submitted by that user:

   * **Execute:** `dlsctl user delete <user_name> -p/--purge`
      

**Note 1:** No data from the Intel DL Studio storage is deleted during this operation.

**Note 2:** The command may take up to 30 seconds to delete the user. A new user with the same user name cannot be created until after the delete command confirms that the first user with the same name has been deleted (see: [Troubleshooting](Z_examples/Troubleshooting) for more details).


