# IMDB sentiment analysis CNN training example

* Training (adjust cpu/memory to environment's capabilities):
```bash
nctl experiment submit imdb_cnn.py  --name imdb-cnn \
-p cpu 4 \
-p memory 2Gi \
--requirements requirements.txt \
-- --output-path /mnt/output/experiment --cpu-count 2
```

* Monitoring training with TensorBoard*:
```bash
nctl launch tb imdb-cnn
```

* Starting prediction instance: 
```bash
nctl predict launch -n imdb-cnn-inference --model-location /mnt/output/imdb-cnn/imdb_tf_model
```

Use prediction instance (**execute steps below in Python virtualenv**):
```bash
pip install -r requirements.txt
python imdb_cnn_vectorize_text.py 'some text that we want to perform sentiment analysis on' > inference_data.json
nctl predict stream --name imdb-cnn-inference --data inference_data.json

```

* Performing hyperparameter optimalization, in this example, we will check how different size of convolutional kernel will perform:
```bash
nctl exp submit imdb_cnn.py -n imdb-cnn-opt \
 -p cpu 4 \
 -p memory 2Gi \
 --requirements requirements.txt \
 --parameter-range '--kernel-size' '{2,3,4}'
 -- --cpu-count 2
```

In order to compare the results, let's use `experiment list` command:
```bash
(.venv) mciesiel@dev:~/nauta/applications/cli$ python main.py exp list -n imdb-cnn-opt
| Name             | Parameters                  | Metrics                      | Submission date        | Start date             | Duration      | Owner     | Status   | Template name     | Template version   |
|------------------+-----------------------------+------------------------------+------------------------+------------------------+---------------+-----------+----------+-------------------+--------------------|
| imdb-cnn-opt-1   | imdb_cnn.py --kernel-size=2 | accuracy: 0.80584            | 2019-03-29 01:36:38 PM | 2019-03-29 01:36:47 PM | 0d 0h 25m 16s | pomidorek | RUNNING  | tf-training-tfjob | 0.1.0              |
|                  |                             | loss: 0.399                  |                        |                        |               |           |          |                   |                    |
|                  |                             | validation_accuracy: 0.8606  |                        |                        |               |           |          |                   |                    |
|                  |                             | validation_loss: 0.320       |                        |                        |               |           |          |                   |                    |
| imdb-cnn-opt-2   | imdb_cnn.py --kernel-size=3 | accuracy: 0.79948            | 2019-03-29 01:36:43 PM | 2019-03-29 01:36:53 PM | 0d 0h 25m 10s | pomidorek | RUNNING  | tf-training-tfjob | 0.1.0              |
|                  |                             | loss: 0.404                  |                        |                        |               |           |          |                   |                    |
|                  |                             | validation_accuracy: 0.87264 |                        |                        |               |           |          |                   |                    |
|                  |                             | validation_loss: 0.299       |                        |                        |               |           |          |                   |                    |
| imdb-cnn-opt-3   | imdb_cnn.py --kernel-size=4 | accuracy: 0.8044             | 2019-03-29 01:36:47 PM | 2019-03-29 01:36:58 PM | 0d 0h 25m 5s  | pomidorek | RUNNING  | tf-training-tfjob | 0.1.0              |
|                  |                             | loss: 0.400                  |                        |                        |               |           |          |                   |                    |
|                  |                             | validation_accuracy: 0.87252 |                        |                        |               |           |          |                   |                    |
|                  |                             | validation_loss: 0.299       |                        |                        |               |           |          |                   |                    |

```

Training script allows customization of multiple other hyperparameters:
```bash
(.venv) mciesiel@mciesiel-mac02:~/Documents/Repos/Nervana/carbon/applications/cli/example-python/package_examples/imdb_sentiment$ python imdb_cnn.py -h
usage: IMDB sentiment classification training script. [-h] [--epochs EPOCHS]
                                                      [--batch-size BATCH_SIZE]
                                                      [--embedding-dims EMBEDDING_DIMS]
                                                      [--filters FILTERS]
                                                      [--kernel-size KERNEL_SIZE]
                                                      [--hidden-dims HIDDEN_DIMS]
                                                      (...)

optional arguments:
  -h, --help            show this help message and exit
  --epochs EPOCHS
  --batch-size BATCH_SIZE
  --embedding-dims EMBEDDING_DIMS
  --filters FILTERS
  --kernel-size KERNEL_SIZE
  --hidden-dims HIDDEN_DIMS
  (...)

```