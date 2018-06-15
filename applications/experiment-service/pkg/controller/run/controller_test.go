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
	"fmt"
	"log"
	"time"

	. "github.com/onsi/ginkgo"
	. "github.com/onsi/gomega"
	"github.com/stretchr/testify/mock"
	core_v1 "k8s.io/api/core/v1"
	meta_v1 "k8s.io/apimachinery/pkg/apis/meta/v1"

	"github.com/nervanasystems/carbon/applications/experiment-service/pkg/apis/aggregator/common"
	run_v1 "github.com/nervanasystems/carbon/applications/experiment-service/pkg/apis/aggregator/v1"
	run_client_v1 "github.com/nervanasystems/carbon/applications/experiment-service/pkg/client/clientset_generated/clientset/typed/aggregator/v1"
)

type runTester struct {
	expectedKey string
	actualKey   string
	actualErr   error
	before      chan struct{}
	after       chan struct{}
	mock        *PodListenerFake
}

var _ = Describe("Run controller", func() {
	var rT *runTester
	var client run_client_v1.RunInterface
	var instance *run_v1.Run

	BeforeEach(func() {
		instance = prepareRun(1)
		client = cs.AggregatorV1().Runs(instance.Namespace)

		rT = new(runTester)
		rT.expectedKey = fmt.Sprintf("%s/%s", instance.Namespace, instance.Name)
		rT.mock = setupPodListerFake()
	})

	JustBeforeEach(func() {
		rT.before = make(chan struct{})
		rT.after = make(chan struct{})
		rT.prepareReconcileCallbacks()
	})

	AfterEach(func() {
		client.Delete(instance.Name, &meta_v1.DeleteOptions{})
		close(rT.before)
		close(rT.after)
	})

	Describe("when creating a new Run", func() {
		It("invoke the reconcile method twice and change the state to RUNNING", func() {
			rT.mock.lister.On("List", mock.Anything).Return([]*core_v1.Pod{prepareRunningPod()}, nil).Twice()

			_, err := client.Create(instance)
			Expect(err).ShouldNot(HaveOccurred())
			rT.verifyReconcileCalls(2, nil)

			// Verify after reconcile
			updatedRun, err := client.Get(instance.Name, meta_v1.GetOptions{})
			Expect(err).ShouldNot(HaveOccurred())
			Expect(updatedRun.Spec.State).To(Equal(common.Running))
			rT.mock.lister.AssertExpectations(GinkgoT())
		})

		It("invoke the reconcile method once and don't change state, if pods are not spawn yet", func() {
			rT.mock.lister.On("List", mock.Anything).Return([]*core_v1.Pod{}, nil).Once()

			_, err := client.Create(instance)
			Expect(err).ShouldNot(HaveOccurred())
			rT.verifyReconcileCalls(1, nil)

			// Verify after reconcile
			updatedRun, err := client.Get(instance.Name, meta_v1.GetOptions{})
			Expect(err).ShouldNot(HaveOccurred())
			Expect(updatedRun.Spec.State).To(Equal(common.RunState("")))
			rT.mock.lister.AssertExpectations(GinkgoT())
		})
	})

	Describe("when updating a Run", func() {
		It("invoke the reconcile method once and don't save it, if no state change", func() {
			instance.Spec.State = common.Complete
			rT.mock.lister.On("List", mock.Anything).
				Return([]*core_v1.Pod{preparePod(core_v1.PodSucceeded)}, nil).Once()

			_, err := client.Update(instance)
			Expect(err).ShouldNot(HaveOccurred())
			rT.verifyReconcileCalls(1, nil)

			// Verify after reconcile
			updatedRun, err := client.Get(instance.Name, meta_v1.GetOptions{})
			Expect(err).ShouldNot(HaveOccurred())
			Expect(updatedRun.Spec.State).To(Equal(common.Complete))
			rT.mock.lister.AssertExpectations(GinkgoT())
		})
	})
})

// Setup test callbacks to be called when the message is reconciled
func (r *runTester) prepareReconcileCallbacks() {
	runCtrl.BeforeReconcile = func(key string) {
		r.actualKey = key
		r.before <- struct{}{}
	}

	runCtrl.AfterReconcile = func(key string, err error) {
		r.actualKey = key
		r.actualErr = err
		r.after <- struct{}{}
	}
}

// Verify reconcile function is called against the correct key
func (r *runTester) verifyReconcileCalls(expectedCalls int, expectedErr error) {
	for i := 0; i < expectedCalls; i++ {
		log.Printf("Processing reconcile %d call", i+1)
		select {
		case <-r.before:
			Expect(r.actualKey).To(Equal(r.expectedKey))
			Expect(r.actualErr).ShouldNot(HaveOccurred())
		case <-time.After(time.Second * 2):
			Fail("reconcile never called")
		}

		select {
		case <-r.after:
			Expect(r.actualKey).To(Equal(r.expectedKey))
			if expectedErr == nil {
				Expect(r.actualErr).ShouldNot(HaveOccurred())
			} else {
				Expect(r.actualErr).To(Equal(expectedErr))
			}

		case <-time.After(time.Second * 2):
			Fail("reconcile never finished")
		}
	}
}
