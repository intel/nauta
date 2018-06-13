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
	"time"

	. "github.com/nervanasystems/carbon/applications/experiment-service/pkg/apis/aggregator/v1"
	. "github.com/nervanasystems/carbon/applications/experiment-service/pkg/client/clientset_generated/clientset/typed/aggregator/v1"
	. "github.com/onsi/ginkgo"
	. "github.com/onsi/gomega"

	core_v1 "k8s.io/api/core/v1"
	meta_v1 "k8s.io/apimachinery/pkg/apis/meta/v1"

	"github.com/nervanasystems/carbon/applications/experiment-service/pkg/apis/aggregator/common"
	"github.com/stretchr/testify/mock"
)

type runTester struct {
	expectedKey string
	actualKey   string
	actualErr   error
	before      chan struct{}
	after       chan struct{}
}

var _ = Describe("Run controller", func() {
	var instance Run
	var client RunInterface
	var rT *runTester

	BeforeEach(func() {
		rT = new(runTester)
		instance = prepareRun()
		rT.expectedKey = "run-controller-test-handler/instance-1"
	})

	JustBeforeEach(func() {
		rT.before = make(chan struct{})
		rT.after = make(chan struct{})
		rT.prepareReconcileCallbacks()
	})

	AfterEach(func() {
		client.Delete(instance.Name, &meta_v1.DeleteOptions{})
	})

	Describe("when creating a new Run", func() {
		It("invoke the reconcile method", func() {
			pod := preparePod()
			testObj := setupPodListerFake()
			testObj.lister.On("List", mock.Anything).Return([]*core_v1.Pod{pod}, nil)
			//testObj.lister.AssertNumberOfCalls()

			client = cs.AggregatorV1().Runs("run-controller-test-handler")

			// Create an instance
			_, err := client.Create(&instance)
			Expect(err).ShouldNot(HaveOccurred())
			rT.verifyReconcileCalls()

			// Verify after reconcile
			updatedRun, err := client.Get(instance.Name, meta_v1.GetOptions{})
			Expect(err).ShouldNot(HaveOccurred())
			Expect(updatedRun.Spec.State).To(Equal(common.Running))
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
func (r *runTester) verifyReconcileCalls() {
	for i := 0; i < 2; i++ {
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
			Expect(r.actualErr).ShouldNot(HaveOccurred())
		case <-time.After(time.Second * 2):
			Fail("reconcile never finished")
		}
	}
}

func preparePod() *core_v1.Pod {
	pod := core_v1.Pod{}
	pod.Name = "kuba"
	pod.Namespace = "run-controller-test-handler"
	pod.Labels = map[string]string{"k": "b"}
	return &pod
}

func prepareRun() Run {
	run := Run{}
	run.Name = "instance-1"
	run.Spec.State = "" //common.Complete
	//instance.Namespace = "run-controller-test-handler"
	run.Spec.PodCount = 1
	run.Spec.PodSelector = meta_v1.LabelSelector{
		MatchLabels: map[string]string{"k": "b"},
	}
	return run
}
