# Working with Datasets

The section covers the following topics:

* Uploading Datasets
* `dlsctl mount` Command
* Mount and Access Folders
* Uploading and Using Shared Dataset Example

## Uploading Datasets

Intel DL Studio offers two ways for users to upload and use datasets for experiments:

### Uploading during experiment submission

Uploading additional datasets or files is an option available for the ‘submit’ command, using the following option:

`-sfl, --script_folder_location`

Where `script_folder_location` is the name of a folder with additional files used by a script, e.g., other .py files, 
datasets, etc. If the option is not included, the files will not be included in the experiment.

**Syntax:**

`dlsctl experiment submit --script_folder_location DATASET-PATH SCRIPT_LOCATION`

This option is recommended for small datasets or datasets that are NOT reused often. In using this option, 
the dataset will be uploaded each time the submit command is executed which may add to the overall submission time.

### Upload to DL Studio storage and reference location

Depending on the Intel DL Studio configuration, the application uses NFS to connect to a storage location where each user 
has folders that have been setup to store experiment input and output data. This option allows the user to upload 
files and datasets for private use and for sharing. Once uploaded, the files are referenced by the  path. All 
data in the folders are retained until the user manually removes it from the NFS storage. Refer to the following 
sections in this chapter for information how to access and use Intel DL Studio storage.

This option is recommended for large datasets, data that will be reused often, and data that will be shared among users.

## dlsctl mount Command

The ‘mount’ command displays another command that can be used to mount Intel DL Studio folders to a user’s local 
machine. When a user executes the command, information similar the following is displayed (this example is for macOS).  Use 
the following command to mount those folders (all of the following is displayed, although this is an example only).
 
![Image](images/dlsctl_mount_command.png)

**Note 1:** The dlsctl mount command also returns a command to unmount a folder.

**Note 2:** Intel DL Studio uses the mount command that is native to each operating system, so the command printed 
out may not appear as in this example.

**Note 3:** All variables are shown in upper case.

## Mount and Access Folders

The following table displays the access permissions for each mounting folder.

Table 1: Access Permissions for Mounting Folders

DLS4E Folder	Reference Path	User Access	Public Access
input	/mnt/input/home	read/write	-
output	/mnt/output/home	read/write	-
input-shared	/mnt/input/root/public	read/write	read/write
output-shared	/mnt/output/root/public	read/write	read/write
input-output-ro	 	read	read

## Uploading and Using Shared Dataset Example

Perform these steps to mount a local folder/machine to Intel DL Studio storage and use the files when performing training.

1. Linux/macOS only: Create a folder for mounting named my-shared-input.

      **Execute**: `mkdir my-shared-input`

2. Use the mount command to display the command that should be used to mount your local folder/machine to your Intel DL Studio input folder.

      **Execute**: `dlsctl mount`

3. Use the mounting command that was displayed to mount your local machine to Intel DL Studio storage. Examples of mounting the 
local folder to the Intel DL Studio output folder for each OS:
   * MacOS: `mount_mbfs //'USERNAME:PASSWORD'@CLUSTER-URL/input-shared my-shared-input`
   * Ubuntu: `sudo mount.cifs -o username=USERNAME,password=PASSWORD,rw,uid=1000 //CLUSTER-URL/input-shared my-shared-input`
   * Windows: Use Y: drive as mount point `net case Y: \\CLUSTER-URL\input-shared /user:USERNAME PASSWORD`

4. **Execute**: the mount command that is provided by dlsctl mount using the input-shared as the DLS4E_FOLDER and my-shared-input 
folder or ‘Y:’ as the MOUNTPOINT.

   **Note**: The command is dependent on the operating system. For Linux/macOS users, you should mount my-shared-input to the storage folder input.

5.	Navigate to the mounted location:
    * MacOS/Ubuntu only: Navigate to my-shared-input folder.
    * Windows: Open Explorer Window and navigate to Y: drive
  
6.	Copy input data or files to this folder for use when submitting experiments. After copying, the files will be located 
in Intel DL Studio storage and can be used by any user for their experiments.

7.	Using the mnist example from [Submitting an Experiment](getting_started.md#submitting-an-experiment), you can follow download the mnist dataset from 
this link: Mnist Dataset: http://yann.lecun.com/exdb/mnist

8.	Create a mnist folder in the Intel DL Studio input-shared folder.

9.	Copy the downloaded files to the folder.

10.	Submit an experiment referencing the new shared dataset. From the examples folder:

    **Execute**:`dlsctl experiment submit --name mnist-shared-input mnist_with_summaries.py -- --data_dir=/mnt/input/root/public/mnist`

11.	Any Intel DL Studio user can use the same path to reference the mnist dataset on your DL Storage. If you are not sure what datasets your team has available, simply mount the input-shared folder and check. Placing data in the input-shared folder lets other users of Intel DL Studio use that data.
