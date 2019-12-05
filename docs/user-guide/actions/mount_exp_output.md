# Mounting Experiment Output to Nauta Storage

To mount a local `folder` to the Nauta storage and use the files when performing training, execute the following steps.

**Note**: The names used below are for example purposes only. Also, refer to [Mount Options](http://man7.org/linux/man-pages/man8/mount.8.html) for more details. 

**Linux/macOS**

1. Create a folder for mounting and name it `my_output` by executing the following command: 
 
   `mkdir my_output`

1. Execute the `mount` command to display the command you should use to mount your local folder to your Nauta ouput folder. 

   `nctl mount`

1. Enter `mount_smbfs` or `mount.cfis` as appropriate. Be aware, these commands are dependent on the operating system you are using. 

   **Note:** The MOUNTPOINT is your `my_output` folder. 

1. Navigate to the `my_output` folder.

1. Use the output folder (`my_output`) to review the results of the training. For example, trained models.

----------------------

## Return to Start of Document

* [README](../README.md)

----------------------

