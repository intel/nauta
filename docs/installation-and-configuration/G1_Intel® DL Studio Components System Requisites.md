# Intel® DL Studio Studio Components System Requisites
Intel DL Studio requires certain components, as shown in Table 1.

## List of Software Components

Table 1 shows the list of components required for DL Studio, which are part of the original package. 


Name | Version | Project link
--- | --- | --- 
flannel | 0.9.1 | https://github.com/coreos/flannel
kube-proxy | 1.10.6 | http://gcr.io/google-containers/kube-proxy-amd64
pause | 3.1 | http://gcr.io/google-containers/pause-amd64
tiller | 2.9.1 | https://github.com/helm/helm
addon-resizer | 1.7 | http://k8s.gcr.io/addon-resizer 
heapster | 1.4.2 | https://github.com/kubernetes/heapster
defaultbackend | 1.4 | https://github.com/kubernetes/ingress-nginx
ingress | 0.14.0 | http://quay.io/kubernetes-ingress-controller/nginx-ingress-controller
kube-dns | 1.14.8 | https://github.com/kubernetes/dns 
dnsmasq-nanny | 1.14.8 | https://github.com/kubernetes/dns
dns-sidecar | 1.14.8 | https://github.com/kubernetes/dns
etcd | 3.3.9 | https://github.com/coreos/etcd
dashboard | 1.8.3 | https://k8s.gcr.io/kubernetes-dashboard-amd64 
registry | 2.6.2 | https://github.com/docker/distribution
kubectl | 1.10.6 | https://github.com/kubernetes/kubernetes/tree/master/pkg/kubectl
elasticsearch | 6.2.3 | https://github.com/elastic/elasticsearch
fluentd | 0.12 | https://www.fluentd.org/
redsocks | 0.5 | https://github.com/darkk/redsocks
tensorflow | 1.9.0 | https://github.com/tensorflow/tensorflow
nginx | 1.14.0 | https://www.nginx.com/
mkl-dnn | 0.14 | https://github.com/intel/mkl-dnn


## Key Components
Key Compponents include: 
* An Optimized HW stack
  * **Note:** Hardware is sold by Dell EMC.
* Intel Deep Learning Studio Enterprise complete bundle (including installation scripts and reference configuration)
  * Vanilla Kubernetes cluster on top of provisioned HW and OS-level SW. 
  * Intel Deep Learning Studio Enterprise components (containerized components, their configuration, integration means, and so  on.)
  * Used SW components are optimized for IA containers with Intel optimized libraries such as: Math Kernel Library (Intel® MKL) for Deep Neural Networks (Intel® MKL-DNN), optimized framework parameters, and so on.

## Inlcluded Documentation
* Installation and Configuration Administration Guide 
  * Format = PDF
* User Guide
  * Format = HTML
* Release Notes
  * Format = HTML & PDF
