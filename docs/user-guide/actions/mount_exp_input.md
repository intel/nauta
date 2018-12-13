# Mounting Experiment Input to Intel DL Studio Storage

Perform these steps to mount a local folder/machine to Intel DL Studio storage and use the files when performing training.

**Note**: Names below are examples only.

1. Linux/macOS: Create a folder for mounting named `my_input`.
 
   **Execute**: `mkdir my_input`

2. Use the mount command to display the command that should be used to mount your local folder/machine to your Intel DL
Studio input folder. 

   **Execute**: `dlsctl mount`

3. **Execute**: `mount_smbfs` or `net use` or `mount.cfis` as appropriate. The command is dependent on the operating system. 
For Linux/macOS users, the MOUNTPOINT is the `my_input` folder. For Windows users, choose a drive letter
as mount point.

4. Linux/macOS only: Navigate to `my_input`
   Windows: Open Explorer Window and navigate to the input/home folder.

5. Copy input data or files to this folder for use when submitting experiments.
