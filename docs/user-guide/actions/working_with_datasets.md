# Working with Datasets

The section discusses the following main topics:

 - [Uploading Dataset](#uploading-datasets)  
 - [nctl mount Command](#nctl-mount-command)
 - [Mounting and Accessing Folders](#mounting-and-accessing-folders)
 - [Uploading and Using Dataset Example](#uploading-and-using-dataset-example)
 - [Uploading and Using Shared Dataset](#uploading-and-using-a-shared-dataset)
 - [Uploading During Experiment Submission](#uploading-during-experiment-submission)
 
## Uploading Datasets

Nauta uses NFS to connect to a storage location where each user has folders that have been setup to store experiment input and output data. This option allows the user to upload files and datasets for private use and for sharing. Once uploaded, the files are referenced by the  path.

All data in the folders are retained until the user manually removes it from the NFS storage. Refer to the [Uploading and Using Dataset Example](#uploading-and-using-dataset-example) in this section for information.

## nctl mount Command

The `mount` command displays another command that can be used to mount Nauta folders to a user’s local 
machine. When a user executes the command, information similar to the following is displayed (the example shown is for macOS only).  

Use the following command to mount those folders (scroll right to see full contents):

`nctl mount`
 
```
|=======================================================================================================|
|   <NAUTA_FOLDER>  |   Code Reference Path     |   User Access     |   Shared Access                   |
|-------------------------------------------------------------------------------------------------------|
|   input           |   /mnt/input/home         |   read/write      |   -                               |
|   output          |   /mnt/output/home        |   read/write      |   -                               |
|   input-shared    |   /mnt/input/root/public  |   read/write      |   read/write                      |
|   output-shared   |   /mnt/output/root/public |   read/write      |   read/write                      |
|   input-output-ro |                           |   read            |   read                            |
|=======================================================================================================|
|   Each experiment has a special folder that can be accessed                                           |
|   as /mnt/output/experiment from training script. This folder is shared by Samba                      |
|   as output/<EXPERIMENT_NAME>.                                                                        |
|=======================================================================================================|
|   <MOUNTPOINT>    |   folder/drive location on your local machine                                     |
|=======================================================================================================|
    
Command to unmount previously mounted folder:
sudo umount <MOUNTPOINT> [-fl]
In case of problems with unmounting (disconnected disk etc.) try out -f (force) or -l (lazy) options. For more info about these options refer to man umount.

Example usage:
    - Mounting a local folder (mylocalfolder) to the user's Nauta input folder:
        sudo mount.cifs -o username=JANEDOE,password=lqS9P5kQ0TFzMmscCY21ZklDDKZtdBeH,rw,uid=10001 //10.91.120.152/input mylocalfolder
    - Code reference path:
        data_dir=/mnt/input/home/<Uploaded-DataFolder>
    - Unmount the folder:
        umount mylocalfolder
```

### Other nctl mount and mount Information

The `nctl mount` command also returns a command to unmount a folder. Nauta uses the mount command that is native to each operating system, so the command printed out _may not_ appear as in this example. In addition, _all variables_ are shown in upper-case.

## Mounting and Accessing Folders

The following table shows the access permissions for each mounting folder.

| Nauta Folder | Reference Path | User Access | Shared Access
|:--- |:--- |:--- |:--- |
| input |	/mnt/input/home |	read/write	| - |
| output |	/mnt/output/home |	read/write |	- |
| input-shared	| /mnt/input/root/public	| read/write |	read/write |
| output-shared	| /mnt/output/root/public |	read/write |	read/write |
| input-output-ro | | read |	read |

## Uploading and Using Dataset Example

The default configuration is to mount local folders to a Nauta user's private input and output storage folders. Execute the the following steps to mount a local folder,`my-input`, to Nauta storage so that input data can be referenced from the storage when performing training.

1. **Linux/macOS only:** Create a folder for mounting named `my-input`folder. 

   `mkdir my-input`

2. Use `nctl mount` to display the mounting command for your operating system.

    `nctl mount`

3. Enter the `mount` command that is provided by `nctl mount`using the input as the NAUTA-FOLDER and my-input folder as the MOUNTPOINT. Examples of mounting the command:

   * **MacOS:** `mount_mbfs //'USERNAME:PASSWORD'@CLUSTER-URL/input`
   * **Ubuntu:** `sudo mount.cifs -o username=USERNAME,password=PASSWORD,rw,uid=1000 //CLUSTER-URL/input`

4.	Navigate to the mounted location:
    * **MacOS/Ubuntu only:** Navigate to my-input folder.
    
5.	Copy a dataset or files to the folder for use in experiments. The files will be located in the Nauta storage until deleted.

6.	Use the MNIST example from [Submitting an Experiment](getting_started.md#submitting-an-experiment), you can download the MNIST dataset using the following link: [THE MNIST DATABASE](http://yann.lecun.com/exdb/mnist)

7.	Create a MNIST folder in the Nauta input folder.

8.	Copy the downloaded files to the folder.

9.	Submit an experiment referencing the new shared dataset. From the nctl home directory, run this command (scroll right to see the full contents):

```
nctl experiment submit --name mnist-input examples/mnist_single_node.py -- --data_dir=/mnt/input/home/MNIST
```

## Uploading and Using a Shared Dataset

If you want to copy your data to a shared folder, use input-shared instead of input in step 3. Using the shared Nauta storage will allow all Nauta users to use the same MNIST dataset by referencing the shared path:

```
/mnt/input/root/public/MNIST
```

## Uploading During Experiment Submission

Uploading additional files is an option available for the `submit` command, using the following option:

`-sfl, --script-folder-location`

Where `script-folder-location` is the name of a folder with additional files used by a script. For example, other `.py` files, assets, and so on.

**Syntax:**

`nctl experiment submit --script-folder-location DATASET-PATH SCRIPT-LOCATION`

This option may be used only for small datasets for development purposes (datasets larger than several MB should be uploaded
using standard mechanism described above). 

**WARNING:** Submitting large amount of data using this option will prolong an experiments' submission time.

----------------------

## Return to Start of Document

* [README](../README.md)
----------------------
