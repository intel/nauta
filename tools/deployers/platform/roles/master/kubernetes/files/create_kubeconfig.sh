#
# Copyright (c) 2019 Intel Corporation
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#

kubectl config set-cluster maas-cluster \
    --certificate-authority=/etc/nauta-cluster/master/kubernetes/ca/CA.crt \
    --embed-certs=true \
    --server=https://$1:$2 \
    --kubeconfig=/etc/nauta-cluster/master/kubernetes/kubeconfigs/$3.kubeconfig

kubectl config set-credentials $4 \
    --client-certificate=/etc/nauta-cluster/master/kubernetes/crt/$3.crt \
    --client-key=/etc/nauta-cluster/master/kubernetes/key/$3.key \
    --embed-certs=true \
    --kubeconfig=/etc/nauta-cluster/master/kubernetes/kubeconfigs/$3.kubeconfig

kubectl config set-context default \
    --cluster=maas-cluster \
    --user=$4 \
    --kubeconfig=/etc/nauta-cluster/master/kubernetes/kubeconfigs/$3.kubeconfig

kubectl config use-context default --kubeconfig=/etc/nauta-cluster/master/kubernetes/kubeconfigs/$3.kubeconfig