# View All User Activity

Use the `nctl user list` command to display all the current users, as well as all of their experiments (with status). Furthermore, the command displays the following information:

  * **Name:** user name
  * **Creation date:** the date this user account was created
  * **Date of last submitted job:** experiment
  * **Number of running jobs:** experiments
  * **Number of queued jobs:** experiments submitted, but not yet running

Administrators _are not_ listed and previously deleted users _are not_ shown. To _create_ a user account, refer to [Creating a User Account](../actions/create_user.md) and to _delete_ a user account, refer to [Deleting a User Account](../actions/delete_user.md). 

Execute the following command:

`nctl user list`

Example results are shown below (scroll right to see the full contents).

```

| Name    | Creation date          | Date of last submitted job   |   Number of running jobs |   Number of queued jobs |
|---------+------------------------+------------------------------+--------------------------+-------------------------|
| user1   | 2019-03-12 08:30:45 PM |  2019-03-02 05:25:14 PM      |                        1 |                       1 | 
| user2   | 2019-03-12 09:50:50 PM |                              |                        0 |                       0 |
| user3   | 2019-03-12 09:51:31 PM |                              |                        0 |                       0 |

```

----------------------

## Return to Start of Document

* [README](../README.md)
----------------------
