# Nauta System Software Components

Nauta relies on the external software components listed in the table below. Links to each of the component's descriptions are included should you need detailed information. These components are included in Nauta, and are  automatically installed as part of the Nauta installation process. 

## List of External Software Components

The following table lists Nauta's external software components and their versions. 

Name | Version | Project link
--- | --- | --- 
addon-resizer | 1.13.6 | https://github.com/kubernetes/autoscaler/tree/master/addon-resizer 
dashboard | 1.8.3 | https://github.com/kubernetes/dashboard
defaultbackend | 1.4 | https://github.com/kubernetes/ingress-nginx
dnsmasq-nanny | 1.14.8 | https://github.com/kubernetes/dns
dns-sidecar | 1.14.8 | https://github.com/kubernetes/dns
etcd | 3.3.13 | https://github.com/coreos/etcd
elasticsearch | 7.3.0 | https://github.com/elastic/elasticsearch
flannel | 0.11.0 | https://github.com/coreos/flannel
fluentd | 1.2.5 | https://www.fluentd.org/
heapster | 1.4.3 | https://github.com/kubernetes/heapster
helm | 2.11.0 | https://github.com/helm/helm
ingress | 0.24.0 | http://quay.io/kubernetes-ingress-controller/nginx-ingress-controller
kubectl | 1.15.3 | https://github.com/kubernetes/kubernetes/tree/master/pkg/kubectl
kube-dns | 1.14.12 | https://github.com/kubernetes/dns 
kube-proxy | 1.15.3 | https://hub.docker.com/r/googlecontainer/kube-proxy-amd64/
mkl-dnn | 0.18 | https://github.com/intel/mkl-dnn
nginx | 1.14.0 | https://www.nginx.com/
openvino | 2019_R1.1 | https://github.com/opencv/dldt
pause | 3.1 | https://hub.docker.com/r/googlecontainer/pause-amd64/
pytorch | 1.2.0 | https://github.com/pytorch/pytorch
redsocks | 0.5 | https://github.com/darkk/redsocks
registry | 2.7 | https://github.com/docker/distribution
tensorflow | 1.12.0 | https://github.com/tensorflow/tensorflow

## Key Components

The Nauta installation package consists of two major components:

1. A package that installs a vanilla Kubernetes cluster, including necessary OS-level software components, on provisioned Hardware.

1. A package that installs Nauta components (including containers, configuration files, and so on) on the above-mentioned Kubernetes cluster.

Nauta software components are optimized for AI containers containing Nauta-optimized libraries.

## Next Steps: How to Build Nauta

* [Building Nauta](../README.md)

----------------------

## Return to Start of Document

* [README](../README.md)

----------------------


