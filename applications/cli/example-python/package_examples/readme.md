Creating experiments from example scripts.


1. Preparing Data

    Each example requires a dataset.  Descriptions on how to download them are available here:
    
    -   alexnet_single_node.py requires small_imagenet dataset
    -   imdb_lstm.py requires lstm_reviews dataset
    -   mnist scripts require mnist dataset
    -   resnet requires small_imagenet_tf dataset

2. Placing experiment data

    There are two options:
    -   First option is to execute
            
            nctl mount
        as a user (administrator cannot do it).  
        The command provides the native mount command for each OS.
        For example, using the command provided for ubuntu, this command will mount the local 'mountFolder' to the Nauta user input folder:
        
            sudo mount.cifs -o username=your_user_name,password=lqS9P5kQ0TFzMmscCY21ZklDDKZtdBeH,rw,uid=10001 //10.91.120.152.nauta.intel.com/input /path/to/mountFolder
    
        Once mounted, place data in /path/to/mountFolder.  The training data will appear on pod in /mnt/input/home.
        Example: /mnt/input/home/small_imagenet
    
    -   Second option is to place data in one directory with script and pass directory path as -sfl (--script-folder-location) parameter.
        Data will appear on pod in /app/ directory. This option is not recommended for datasets larger than 1 MB.
    Note: For more information on mounting or datasets, see 'Working with Datasets' section of the User Guide.  

3. Scripts parameters and execution commands

    -   alexnet_single_node.py
        -    --data_dir, default value: ./dataset/imagenet (actually /app/dataset/imagenet) - Directory which contains dataset
        -    --training_epoch, default value: 1 - Number of training epochs
        -    --batch_size, default value: 128 - Size of image batches
        -    --export_dir, default value: ./output (which will be /app/output) - Export directory for model  
    
        Run using mounted data:
        
            nctl exp submit alexnet/alexnet_single_node.py -sfl alexnet -n alexnet -- --data_dir /mnt/input/home/small_imagenet --batch_size 16 --export_dir /mnt/output/home/alexnet
            
        alexnet directory passed as -sfl contains alexnet_single_node.py and alexnet_model.py
        Run using local data:
        
            nctl exp submit alexnet/alexnet_single_node.py -sfl alexnet -n alexnet -- --data_dir /app/small_imagenet --batch_size 16 --export_dir /mnt/output/home/alexnet
            
        Note: For this command, the alexnet directory must have also contain the small_imagenet dataset folder

   -    imdb_lstm.py
        -   --data_dir, default value: ./dataset/imdb(actually /app/dataset/imdb) - Directory which contains dataset
        -   --export_dir, no default value - Export directory for model
        -   batch_size and number of epochs (iterations) cannot be passed as parameters. They need to be changed inside the scripts (BATCH_SIZE and ITERATIONS consts).
   
        Run using mounted data:
        
            nctl exp submit examples/imdb_lstm.py -n imdb -- --data_dir /mnt/input/home/lstm_reviews --export_dir /mnt/output/home/imdb
            
        Note: -sfl parameter is not passed because script does not require additional scripts
        Run using local data:
        
            nctl exp submit examples/imdb_lstm.py -sfl lstm_data -n imdb -- --data_dir /app/lstm_reviews --export_dir /mnt/output/home/imdb
            
        Note: For this command, the local lstm_data folder must contain the lstm_reviews dataset folder

   -    imagenet_main.py
        -   --data_dir, no default value - Directory which contains dataset
        -   --resnet_size, default value: 50, options[18, 34, 50, 101, 152, 200] - size of resnet
        -   --export_dir, no default value - Export directory for model
    
        Run using mounted data:
        
            nctl exp submit examples/resnet/imagenet_main.py -sfl examples/resnet -n resnet -- --data_dir /mnt/input/home/small_imagenet_tf --export_dir /mnt/output/home/resnet
            
        Run using local data:
        
            nctl exp submit examples/resnet/imagenet_main.py -sfl examples/resnet -n resnet -- --data_dir /app/small_imagenet_tf --export_dir /mnt/output/home/resnet
            
        Note: For this command, the local examples/reset folder must contain the small_imagenet_tf dataset folder
