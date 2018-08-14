package main

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

func NewPodListerFake() *PodListenerFake {
	out := &PodListenerFake{
		lister: &PodNamespaceListerFake{},
	}
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
