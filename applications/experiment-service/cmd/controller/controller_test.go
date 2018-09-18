package main

import (
	"errors"
	"fmt"

	. "github.com/onsi/ginkgo"
	. "github.com/onsi/gomega"
	"github.com/stretchr/testify/mock"
	core_v1 "k8s.io/api/core/v1"
	k8sErrors "k8s.io/apimachinery/pkg/api/errors"
	"k8s.io/apimachinery/pkg/runtime"
	"k8s.io/apimachinery/pkg/runtime/schema"
	"k8s.io/client-go/testing"
	"k8s.io/client-go/util/workqueue"

	"github.com/nervanasystems/carbon/applications/experiment-service/pkg/apis/aggregator/common"
	run_v1 "github.com/nervanasystems/carbon/applications/experiment-service/pkg/apis/aggregator/v1"
	fake_run "github.com/nervanasystems/carbon/applications/experiment-service/pkg/client/clientset/versioned/fake"
)

type runUnitTester struct {
	ctrl            *Controller
	mock            testing.Fake
	runInstance     *run_v1.Run
	pod             *core_v1.Pod
	podListenerMock *PodListenerFake
}

var _ = Describe("Controller", func() {
	var rUT *runUnitTester

	JustBeforeEach(func() {
		rUT = new(runUnitTester)
		rUT.mock = testing.Fake{}
		rUT.podListenerMock = NewPodListerFake()

		rUT.ctrl = &Controller{
			workqueue: workqueue.NewNamedRateLimitingQueue(workqueue.DefaultControllerRateLimiter(), "Runs"),
			podLister: rUT.podListenerMock,
		}

		rUT.runInstance = prepareRun(1)
		rUT.pod = prepareRunningPod()
	})

	Describe("when calling updateState method", func() {
		It("it saves run with success", func() {
			counter := 0
			updateRunMock := func(action testing.Action) (handled bool, ret runtime.Object, err error) {
				counter++
				return true, rUT.runInstance, nil
			}
			rUT.mock.AddReactor("patch", "runs", updateRunMock)
			rUT.ctrl.runclientset = &fake_run.Clientset{Fake: rUT.mock}

			patch := createUpdateStatePatch(common.Complete)
			err := rUT.ctrl.updateRun(rUT.runInstance, []patchSpec{patch})

			Expect(err).ShouldNot(HaveOccurred())
			Expect(counter).Should(Equal(1))
		})

		It("it returns error if run patch without success", func() {
			updateErr := errors.New("update Run error")
			counter := 0
			patchRunMock := func(action testing.Action) (handled bool, ret runtime.Object, err error) {
				counter++
				return true, nil, updateErr
			}
			getRunMock := func(action testing.Action) (handled bool, ret runtime.Object, err error) {
				return true, prepareRun(1), nil
			}

			rUT.mock.AddReactor("patch", "runs", patchRunMock)
			rUT.mock.AddReactor("get", "runs", getRunMock)
			rUT.ctrl.runclientset = &fake_run.Clientset{Fake: rUT.mock}

			patch := createUpdateStatePatch(common.Complete)
			err := rUT.ctrl.updateRun(rUT.runInstance, []patchSpec{patch})

			Expect(err).To(Equal(updateErr))
			Expect(counter).Should(Equal(1))
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

		It("it does not return Failed status if no there is more pods then run specifies", func() {
			result := calculateRunState(prepareRun(1), []*core_v1.Pod{prepareRunningPod(), prepareRunningPod()})
			Expect(result).To(Equal(common.Running))
		})
	})

	Describe("when calling handleObject method", func() {
		It("it returns proper run name", func() {
			counter := 0
			getRunMock := func(action testing.Action) (handled bool, ret runtime.Object, err error) {
				counter++
				return true, prepareRun(1), nil
			}
			rUT.mock.AddReactor("get", "runs", getRunMock)
			rUT.ctrl.runclientset = &fake_run.Clientset{Fake: rUT.mock}

			rUT.ctrl.handleObject(rUT.pod)
			Expect(counter).Should(Equal(1))
		})

		It("it not enqueue run it can not parse Pod", func() {
			counter := 0
			getRunMock := func(action testing.Action) (handled bool, ret runtime.Object, err error) {
				counter++
				return true, prepareRun(1), nil
			}
			rUT.mock.AddReactor("get", "runs", getRunMock)
			rUT.ctrl.runclientset = &fake_run.Clientset{Fake: rUT.mock}

			rUT.ctrl.handleObject(string("bad object"))
			Expect(counter).Should(Equal(0))
		})
	})

	Describe("when calling syncHandler method", func() {
		It("it returns proper run name", func() {
			counter := 0
			getRunMock := func(action testing.Action) (handled bool, ret runtime.Object, err error) {
				counter++
				return true, prepareRun(1), nil
			}
			rUT.mock.AddReactor("get", "runs", getRunMock)
			rUT.ctrl.runclientset = &fake_run.Clientset{Fake: rUT.mock}

			rUT.podListenerMock.lister.On("List", mock.Anything).Return([]*core_v1.Pod{rUT.pod}, nil).Once()

			err := rUT.ctrl.syncHandler(rUT.runInstance.Namespace + "/" + rUT.runInstance.Name)
			Expect(err).ShouldNot(HaveOccurred())
			Expect(counter).Should(Equal(1))
			rUT.podListenerMock.lister.AssertExpectations(GinkgoT())
		})

		It("skips run when not enough pods yet", func() {
			counter := 0
			getRunMock := func(action testing.Action) (handled bool, ret runtime.Object, err error) {
				counter++
				return true, prepareRun(1), nil
			}
			rUT.mock.AddReactor("get", "runs", getRunMock)
			rUT.ctrl.runclientset = &fake_run.Clientset{Fake: rUT.mock}

			rUT.podListenerMock.lister.On("List", mock.Anything).Return([]*core_v1.Pod{}, nil).Once()

			err := rUT.ctrl.syncHandler(rUT.runInstance.Namespace + "/" + rUT.runInstance.Name)

			Expect(err).ShouldNot(HaveOccurred())
			Expect(counter).Should(Equal(1))
			rUT.podListenerMock.lister.AssertExpectations(GinkgoT())
		})

		It("returns error when resource key is invalid", func() {
			err := rUT.ctrl.syncHandler("very/bad/key/format")
			Expect(err).Should(HaveOccurred())
			Expect(err).To(Equal(fmt.Errorf("unexpected key format: %q", "very/bad/key/format")))
		})

		It("returns error when get runs fails", func() {
			getError := errors.New("run error")
			getRunMock := func(action testing.Action) (handled bool, ret runtime.Object, err error) {
				return true, nil, getError
			}
			rUT.mock.AddReactor("get", "runs", getRunMock)
			rUT.ctrl.runclientset = &fake_run.Clientset{Fake: rUT.mock}

			err := rUT.ctrl.syncHandler(rUT.runInstance.Namespace + "/" + rUT.runInstance.Name)
			Expect(err).Should(HaveOccurred())
			Expect(err).To(Equal(getError))
		})

		It("returns error when get podLister fails", func() {
			getRunMock := func(action testing.Action) (handled bool, ret runtime.Object, err error) {
				return true, prepareRun(1), nil
			}
			rUT.mock.AddReactor("get", "runs", getRunMock)
			rUT.ctrl.runclientset = &fake_run.Clientset{Fake: rUT.mock}

			getPodError := errors.New("pod error")
			rUT.podListenerMock.lister.On("List", mock.Anything).Return([]*core_v1.Pod{rUT.pod}, getPodError).Once()

			err := rUT.ctrl.syncHandler(rUT.runInstance.Namespace + "/" + rUT.runInstance.Name)
			Expect(err).Should(HaveOccurred())
			Expect(err).To(Equal(getPodError))
			rUT.podListenerMock.lister.AssertExpectations(GinkgoT())
		})

		It("it not update COMPLETED run again", func() {
			counter := 0
			getRunMock := func(action testing.Action) (handled bool, ret runtime.Object, err error) {
				counter++
				rUT.runInstance.Spec.State = common.Complete
				return true, rUT.runInstance, nil
			}
			rUT.mock.AddReactor("get", "runs", getRunMock)

			updateCounter := 0
			updateRunMock := func(action testing.Action) (handled bool, ret runtime.Object, err error) {
				updateCounter++
				return true, rUT.runInstance, nil
			}
			rUT.mock.AddReactor("patch", "runs", updateRunMock)
			rUT.ctrl.runclientset = &fake_run.Clientset{Fake: rUT.mock}

			//rUT.podListenerMock.lister.On("List", mock.Anything).Return([]*core_v1.Pod{rUT.pod}, nil).Once()

			err := rUT.ctrl.syncHandler(rUT.runInstance.Namespace + "/" + rUT.runInstance.Name)
			Expect(err).ShouldNot(HaveOccurred())
			Expect(counter).Should(Equal(1))
			Expect(updateCounter).Should(Equal(0))
			//rUT.podListenerMock.lister.AssertExpectations(GinkgoT())
		})

		It("returns when run disappears suddenly", func() {
			counter := 0
			getRunMock := func(action testing.Action) (handled bool, ret runtime.Object, err error) {
				counter++
				return true, nil, k8sErrors.NewNotFound(schema.GroupResource{}, "run")
			}
			rUT.mock.AddReactor("get", "runs", getRunMock)

			rUT.ctrl.runclientset = &fake_run.Clientset{Fake: rUT.mock}

			err := rUT.ctrl.syncHandler(rUT.runInstance.Namespace + "/" + rUT.runInstance.Name)
			Expect(err).ShouldNot(HaveOccurred())
			Expect(counter).Should(Equal(1))
		})

		It("does not update run with same status", func() {
			counter := 0
			getRunMock := func(action testing.Action) (handled bool, ret runtime.Object, err error) {
				counter++
				rUT.runInstance.Spec.State = common.Running
				return true, rUT.runInstance, nil
			}
			rUT.mock.AddReactor("get", "runs", getRunMock)

			updateCounter := 0
			updateRunMock := func(action testing.Action) (handled bool, ret runtime.Object, err error) {
				updateCounter++
				return true, rUT.runInstance, nil
			}
			rUT.mock.AddReactor("patch", "runs", updateRunMock)
			rUT.ctrl.runclientset = &fake_run.Clientset{Fake: rUT.mock}

			rUT.podListenerMock.lister.On("List", mock.Anything).Return([]*core_v1.Pod{rUT.pod}, nil).Once()

			err := rUT.ctrl.syncHandler(rUT.runInstance.Namespace + "/" + rUT.runInstance.Name)
			Expect(err).ShouldNot(HaveOccurred())
			Expect(counter).Should(Equal(1))
			Expect(updateCounter).Should(Equal(0))
			rUT.podListenerMock.lister.AssertExpectations(GinkgoT())
		})
	})
})
