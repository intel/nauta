# Mounting Experiment Input to Nauta Storage

Perform these steps to mount a local `folder/machine` to Nauta storage and use the files when performing training.

**Note**: The names used below are for example purposes only.

1. **Linux/macOS** Create a folder for mounting named `my_input`.
 
   `mkdir my_input`

1. Use the mount command to display the command that should be used to mount your local folder/machine to your Nauta input folder. 

   `nctl mount`

1. Enter `mount_smbfs` or `net use` or `mount.cfis` as appropriate. The command is dependent on the operating system. 

1. **Linux/macOS** For Linux/macOS users, the MOUNTPOINT is the `my_input` folder. 

1. **Linux/macOS only**: Navigate to `my_input`

1. Copy the input data or files to this folder for use when submitting experiments.

----------------------

## Return to Start of Document

* [README](../README.md)

----------------------
 
