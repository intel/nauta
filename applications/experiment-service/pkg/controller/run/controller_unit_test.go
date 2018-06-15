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
	"errors"
	"fmt"

	. "github.com/onsi/ginkgo"
	. "github.com/onsi/gomega"
	core_v1 "k8s.io/api/core/v1"
	"k8s.io/apimachinery/pkg/runtime"
	fake_v1 "k8s.io/client-go/testing"

	"github.com/nervanasystems/carbon/applications/experiment-service/pkg/apis/aggregator/common"
	run_v1 "github.com/nervanasystems/carbon/applications/experiment-service/pkg/apis/aggregator/v1"
	fake_run "github.com/nervanasystems/carbon/applications/experiment-service/pkg/client/clientset_generated/clientset/typed/aggregator/v1/fake"
)

type runUnitTester struct {
	ctrl        *RunControllerImpl
	mock        fake_v1.Fake
	runInstance *run_v1.Run
	pod         *core_v1.Pod
}

var _ = Describe("Unit Tests of RunControllerImpl", func() {
	var rUT *runUnitTester

	JustBeforeEach(func() {
		rUT = new(runUnitTester)
		rUT.mock = fake_v1.Fake{}
		rUT.ctrl = &RunControllerImpl{}
		rUT.ctrl.runClient = &fake_run.FakeAggregatorV1{Fake: &rUT.mock}
		rUT.runInstance = prepareRun(1)
		rUT.pod = prepareRunningPod()
	})

	Describe("when calling saveWithRetries method", func() {
		It("it saves run with success", func() {
			updateRunMock := func(action fake_v1.Action) (handled bool, ret runtime.Object, err error) {
				return true, rUT.runInstance, nil
			}
			rUT.mock.AddReactor("update", "runs", updateRunMock)

			err := rUT.ctrl.saveWithRetries(rUT.runInstance, common.Complete, []*core_v1.Pod{rUT.pod})
			Expect(err).ShouldNot(HaveOccurred())
			Expect(rUT.runInstance.Spec.State).To(Equal(common.Complete))
		})

		It("it does not save the run if state is not changed", func() {
			counter := 0
			updateRunMock := func(action fake_v1.Action) (handled bool, ret runtime.Object, err error) {
				counter++
				return true, rUT.runInstance, nil
			}
			rUT.mock.AddReactor("update", "runs", updateRunMock)

			rUT.runInstance.Spec.State = common.Complete
			err := rUT.ctrl.saveWithRetries(rUT.runInstance, common.Complete, []*core_v1.Pod{rUT.pod})
			Expect(err).ShouldNot(HaveOccurred())
			Expect(counter).Should(Equal(0))
			Expect(rUT.runInstance.Spec.State).To(Equal(common.Complete))
		})

		It("it returns error if retries run out without success", func() {
			updateErr := errors.New("update Run error")
			counter := 0
			updateRunMock := func(action fake_v1.Action) (handled bool, ret runtime.Object, err error) {
				counter++
				return true, nil, updateErr
			}
			getRunMock := func(action fake_v1.Action) (handled bool, ret runtime.Object, err error) {
				return true, prepareRun(1), nil
			}

			rUT.mock.AddReactor("update", "runs", updateRunMock)
			rUT.mock.AddReactor("get", "runs", getRunMock)

			err := rUT.ctrl.saveWithRetries(rUT.runInstance, common.Complete, []*core_v1.Pod{rUT.pod})
			expectedErr := errors.New(fmt.Sprintf("Run %s update FAILED! No more save tries left! Error: %s",
				rUT.runInstance.Name, updateErr))
			Expect(err).To(Equal(expectedErr))
			Expect(counter).Should(Equal(3))
		})
	})

	Describe("when calling calculateRunState method", func() {
		It("it returns Running status if all pods are running", func() {
			result := calculateRunState(prepareRun(1), []*core_v1.Pod{prepareRunningPod()})
			Expect(result).To(Equal(common.Running))
		})

		It("it returns Queued status if any of pods is pending", func() {
			result := calculateRunState(prepareRun(2),
				[]*core_v1.Pod{prepareRunningPod(), preparePod(core_v1.PodPending)})
			Expect(result).To(Equal(common.Queued))
		})

		It("it returns Complete status if all pods are succeeded", func() {
			result := calculateRunState(prepareRun(2),
				[]*core_v1.Pod{preparePod(core_v1.PodSucceeded), preparePod(core_v1.PodSucceeded)})
			Expect(result).To(Equal(common.Complete))
		})

		It("it returns Failed status if any of pods is failed", func() {
			result := calculateRunState(prepareRun(2),
				[]*core_v1.Pod{prepareRunningPod(), preparePod(core_v1.PodFailed)})
			Expect(result).To(Equal(common.Failed))
		})

		It("it returns Failed status if no there is no pods", func() {
			result := calculateRunState(prepareRun(1), []*core_v1.Pod{})
			Expect(result).To(Equal(common.Failed))
		})

		It("it returns Failed status if no there is more pods then run specifies", func() {
			result := calculateRunState(prepareRun(1), []*core_v1.Pod{prepareRunningPod(), prepareRunningPod()})
			Expect(result).To(Equal(common.Failed))
		})
	})

	Describe("when calling getReconcileKey method", func() {
		It("it returns proper run name", func() {
			result, err := rUT.ctrl.getReconcileKey(rUT.pod)
			Expect(err).ShouldNot(HaveOccurred())
			expectedResult := fmt.Sprintf("%s/%s", rUT.pod.Namespace, rUT.pod.Labels["runName"])
			Expect(result).To(Equal(expectedResult))
		})

		It("it returns empty string if pod doesn't refers to Run object", func() {
			rUT.pod.Labels = map[string]string{}
			result, err := rUT.ctrl.getReconcileKey(rUT.pod)
			Expect(err).ShouldNot(HaveOccurred())
			Expect(result).To(Equal(""))
		})
	})
})
