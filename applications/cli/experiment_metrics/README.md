# Experiment-metrics library

Library exposes the method that stores training's metrics in Run resources. It can be used
by training jobs run on nauta or locally - on client's machine. The difference between these
two types of execution is that in first case metrics are stored in cluter's resources and
in the second case - metrics are sent to logs. Information, how to configure logs can
be found in the [configuration](#configuration) section.

## Installation

### Installation from source
1. Go to directory with the library which is placed in `nauta` repository under `applications/cli/experiment_metrics`
1. Build new package: `python setup.py sdist`
1. Install prepared packages (use proper `pip`/`pip3` version according to your python version): `pip install ./dist/experiment_metrics-0.0.1.tar.gz`

### Installation from nctl pack
1. Go to directory with the library (its delivered with `nctl` pack under `lib`)
1. Install prepared packages (use proper `pip`/`pip3` version according to your python version): `pip install experiment_metrics-0.0.1.tar.gz`

## Usage
1. In your `.py` file import `publish` method: `from experiment_metrics.api import publish`
1. Start sending metrics of your training, by using `publish(metrics: Dict[str,str])` method

## Configuration

If library is used by o program executed outside of a nauta cluster, metrics are sent to logs
via _logging_ library. Library uses _root_ logger - so if a user wants to send logs to location
other than default for this logger, he/she should configure it before the first call of 
`publish()` method. Below is a simple example how it could be done:



<!-- language: lang-py -->
    from experiment_metrics.api import publish
    
    if __name__ == '__main__':
        for i in range (0, 100):
            metrics = {
                "accuracy_step": str(i)
            }
            publish(metrics)
