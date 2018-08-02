/*
INTEL CONFIDENTIAL
Copyright (c) 2018 Intel Corporation

The source code contained or described herein and all documents related to
the source code ("Material") are owned by Intel Corporation or its suppliers
or licensors. Title to the Material remains with Intel Corporation or its
suppliers and licensors. The Material contains trade secrets and proprietary
and confidential information of Intel or its suppliers and licensors. The
Material is protected by worldwide copyright and trade secret laws and treaty
provisions. No part of the Material may be used, copied, reproduced, modified,
published, uploaded, posted, transmitted, distributed, or disclosed in any way
without Intel's prior express written permission.
No license under any patent, copyright, trade secret or other intellectual
property right is granted to or conferred upon you by disclosure or delivery
of the Materials, either expressly, by implication, inducement, estoppel or
otherwise. Any license under such intellectual property rights must be express
and approved by Intel in writing.
*/

package run

import (
	"github.com/stretchr/testify/mock"
	"k8s.io/api/core/v1"
	"k8s.io/apimachinery/pkg/labels"
	listers_v1 "k8s.io/client-go/listers/core/v1"
)

type PodListenerFake struct {
	mock.Mock
	lister *PodNamespaceListerFake
}

func setupPodListerFake() *PodListenerFake {
	out := &PodListenerFake{
		lister: &PodNamespaceListerFake{},
	}
	podLister = out
	return out
}

func (p *PodListenerFake) List(selector labels.Selector) (ret []*v1.Pod, err error) {
	args := p.Called(selector)
	return args.Get(0).([]*v1.Pod), args.Error(1)
}

func (p *PodListenerFake) Pods(namespace string) listers_v1.PodNamespaceLister {
	return p.lister
}

type PodNamespaceListerFake struct {
	mock.Mock
}

func (p PodNamespaceListerFake) List(selector labels.Selector) (ret []*v1.Pod, err error) {
	args := p.Called(selector)
	return args.Get(0).([]*v1.Pod), args.Error(1)
}

func (p PodNamespaceListerFake) Get(name string) (*v1.Pod, error) {
	args := p.Called(name)
	return args.Get(0).(*v1.Pod), args.Error(1)
}
