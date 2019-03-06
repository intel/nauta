# View All User Activity

The command `nctl user list` displays all current users and all of their experiments (with status).  Furthermore, the command shows the following information:

  * **Name:** user name
  * **Creation date:** the date this user account was created
  * **Date of last submitted job:** experiment
  * **Number of running jobs:** experiments
  * **Number of queued jobs:** experiments submitted but not yet running

Administrators _are not_ listed. Previously deleted users _are not shown_. Enter the following command:

`$ nctl user list`

The following are example results (not all columns are shown).

![](images/user_list.png)



