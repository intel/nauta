/*
Copyright 2018 Intel Corporation.
Copyright The Kubernetes Authors.

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

    http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.
*/

package main

import (
	"encoding/json"
	"fmt"
	"log"
	"time"

	corev1 "k8s.io/api/core/v1"
	"k8s.io/apimachinery/pkg/api/errors"
	metav1 "k8s.io/apimachinery/pkg/apis/meta/v1"
	"k8s.io/apimachinery/pkg/types"
	"k8s.io/apimachinery/pkg/util/runtime"
	"k8s.io/apimachinery/pkg/util/wait"
	coreinformers "k8s.io/client-go/informers/core/v1"
	"k8s.io/client-go/kubernetes"
	corelisters "k8s.io/client-go/listers/core/v1"
	"k8s.io/client-go/tools/cache"
	"k8s.io/client-go/util/workqueue"

	"github.com/nervanasystems/carbon/applications/experiment-service/pkg/apis/aggregator/common"
	"github.com/nervanasystems/carbon/applications/experiment-service/pkg/apis/aggregator/v1"
	clientset "github.com/nervanasystems/carbon/applications/experiment-service/pkg/client/clientset/versioned"
)

// Controller is the controller implementation for Run resources
type Controller struct {
	// kubeclientset is a standard kubernetes clientset
	kubeclientset kubernetes.Interface
	// runclientset is a clientset for our own API group
	runclientset clientset.Interface

	podLister corelisters.PodLister
	podSynced cache.InformerSynced

	// workqueue is a rate limited work queue. This is used to queue work to be
	// processed instead of performing it as soon as a change happens. This
	// means we can ensure we only process a fixed amount of resources at a
	// time, and makes it easy to ensure we are never processing the same item
	// simultaneously in two different workers.
	workqueue workqueue.RateLimitingInterface
}

// NewController returns a new run controller
func NewController(
	kubeclientset kubernetes.Interface,
	runclientset clientset.Interface,
	podInformer coreinformers.PodInformer) *Controller {

	controller := &Controller{
		kubeclientset: kubeclientset,
		runclientset:  runclientset,
		podLister:     podInformer.Lister(),
		podSynced:     podInformer.Informer().HasSynced,
		workqueue:     workqueue.NewNamedRateLimitingQueue(workqueue.DefaultControllerRateLimiter(), "Runs"),
	}

	// Set up an event handler for when Pod resources change.
	// This handler will lookup the owner of the given Pod,
	// and if it is owned by a Run resource will enqueue that Run resource for processing.
	// More info on this pattern:
	// https://github.com/kubernetes/community/blob/8cafef897a22026d42f5e5bb3f104febe7e29830/contributors/devel/controllers.md
	podInformer.Informer().AddEventHandler(cache.ResourceEventHandlerFuncs{
		AddFunc: controller.handleObject,
		UpdateFunc: func(old, new interface{}) {
			newPod := new.(*corev1.Pod)
			oldPod := old.(*corev1.Pod)
			if newPod.ResourceVersion == oldPod.ResourceVersion {
				// Two different versions of the same Pod will always have different RVs.
				return
			}
			controller.handleObject(new)
		},
		// TODO do we want to observer delete action?
		DeleteFunc: controller.handleObject,
	})

	return controller
}

// Run will set up the event handlers for types we are interested in, as well
// as syncing informer caches and starting workers. It will block until stopCh
// is closed, at which point it will shutdown the workqueue and wait for
// workers to finish processing their current work items.
func (c *Controller) Run(threadiness int, stopCh <-chan struct{}) error {
	defer runtime.HandleCrash()
	defer c.workqueue.ShutDown()

	// Start the informer factories to begin populating the informer caches
	log.Println("Starting Run controller")

	// Wait for the caches to be synced before starting workers
	log.Println("Waiting for informer caches to sync")
	if ok := cache.WaitForCacheSync(stopCh, c.podSynced); !ok {
		return fmt.Errorf("failed to wait for caches to sync")
	}

	log.Println("Starting workers")
	// Launch workers to process Run resources
	for i := 0; i < threadiness; i++ {
		go wait.Until(c.runWorker, time.Second, stopCh)
	}

	log.Println("Started workers")
	<-stopCh
	log.Println("Shutting down workers")
	return nil
}

// runWorker is a long-running function that will continually call the
// processNextWorkItem function in order to read and process a message on the
// workqueue.
func (c *Controller) runWorker() {
	for c.processNextWorkItem() {
	}
}

// processNextWorkItem will read a single work item off the workqueue and
// attempt to process it, by calling the syncHandler.
func (c *Controller) processNextWorkItem() bool {
	obj, shutdown := c.workqueue.Get()

	if shutdown {
		return false
	}

	// We wrap this block in a func so we can defer c.workqueue.Done.
	err := func(obj interface{}) error {
		// We call Done here so the workqueue knows we have finished
		// processing this item. We also must remember to call Forget if we
		// do not want this work item being re-queued. For example, we do
		// not call Forget if a transient error occurs, instead the item is
		// put back on the workqueue and attempted again after a back-off
		// period.
		defer c.workqueue.Done(obj)
		var key string
		var ok bool
		// We expect strings to come off the workqueue. These are of the
		// form namespace/name. We do this as the delayed nature of the
		// workqueue means the items in the informer cache may actually be
		// more up to date that when the item was initially put onto the
		// workqueue.
		if key, ok = obj.(string); !ok {
			// As the item in the workqueue is actually invalid, we call
			// Forget here else we'd go into a loop of attempting to
			// process a work item that is invalid.
			c.workqueue.Forget(obj)
			runtime.HandleError(fmt.Errorf("expected string in workqueue but got %#v", obj))
			return nil
		}
		// Run the syncHandler, passing it the namespace/name string of the Run resource to be synced.
		if err := c.syncHandler(key); err != nil {
			return fmt.Errorf("error syncing '%s': %s", key, err.Error())
		}
		// Finally, if no error occurs we Forget this item so it does not
		// get queued again until another change happens.
		c.workqueue.Forget(obj)
		log.Printf("Successfully synced '%s'", key)
		return nil
	}(obj)

	if err != nil {
		runtime.HandleError(err)
		return true
	}

	return true
}

// syncHandler compares the actual state with the desired, and attempts to
// converge the two. It then updates the Status block of the Foo resource
// with the current status of the resource.
func (c *Controller) syncHandler(key string) error {
	// Convert the namespace/name string into a distinct namespace and name
	namespace, name, err := cache.SplitMetaNamespaceKey(key)
	if err != nil {
		runtime.HandleError(fmt.Errorf("invalid resource key: %s", key))
		return nil
	}

	// Get the Run resource with this namespace/name
	run, err := c.runclientset.AggregatorV1().Runs(namespace).Get(name, metav1.GetOptions{})
	if err != nil {
		// The Run resource may no longer exist, in which case we stop processing.
		if errors.IsNotFound(err) {
			runtime.HandleError(fmt.Errorf("run '%s' in work queue no longer exists", key))
			return nil
		}
		return err
	}

	log.Printf("Processing Run: %s. State: %v", run.Name, run.Spec.State)

	selector, err := metav1.LabelSelectorAsSelector(&run.Spec.PodSelector)
	if err != nil {
		runtime.HandleError(fmt.Errorf("run: %s. Convert LabelSelector to Selector Fail: %v", run.Name, err))
		return err
	}

	pods, err := c.podLister.Pods(run.Namespace).List(selector)
	if err != nil {
		runtime.HandleError(fmt.Errorf("run: %s. List pod error: %v", run.Name, err))
		return err
	}

	if run.Spec.State == common.Complete || run.Spec.State == common.Failed || run.Spec.State == common.Cancelled {
		runtime.HandleError(fmt.Errorf("SKIPPING. Run: %s already processed. Final status %v",
			run.Name, run.Spec.State))
		return nil
	}

	if run.Spec.State == "" && len(pods) < run.Spec.PodCount {
		runtime.HandleError(fmt.Errorf("SKIPPING. Run: %s NOT READY to start yet. Not enough pods. "+
			"Required %d, currently: %d", run.Name, run.Spec.PodCount, len(pods)))
		return nil
	}

	stateToSet := calculateRunState(run, pods)
	return c.updateState(run, stateToSet, pods)
}

type statePatchSpec struct {
	Op    string          `json:"op"`
	Path  string          `json:"path"`
	Value common.RunState `json:"value"`
}

func (c *Controller) updateState(run *v1.Run, stateToSet common.RunState, pods []*corev1.Pod) error {
	if run.Spec.State != stateToSet {
		statePatch := []statePatchSpec{
			{
				Op:    "add",
				Path:  "/spec/state",
				Value: stateToSet,
			},
		}

		patchBytes, errMarshal := json.Marshal(statePatch)
		if errMarshal != nil {
			runtime.HandleError(fmt.Errorf("run %s prepare patch error: %v", run.Name, errMarshal))
			return errMarshal
		}

		_, err := c.runclientset.AggregatorV1().Runs(run.Namespace).Patch(run.Name, types.JSONPatchType, patchBytes)
		if err != nil {
			runtime.HandleError(fmt.Errorf("run %s patch FAILED! Error: %v", run.Name, err))
			return err
		}
		run.Spec.State = stateToSet
		return nil
	}

	log.Printf("Run: %s state (%v) not changed. Update no required", run.Name, run.Spec.State)
	return nil
}

func calculateRunState(run *v1.Run, pods []*corev1.Pod) common.RunState {
	var stateToSet common.RunState
	if len(pods) == run.Spec.PodCount {
		stateToSet = calculateRunStateFromPods(pods, run.Name)
		log.Printf("Run %s. New calculated state: %v", run.Name, stateToSet)
	} else if len(pods) == 0 {
		log.Printf("No Pods found. Setting FAILED status for Run: %s", run.Name)
		stateToSet = common.Failed
	} else {
		log.Printf("Incorrect number of Pods found: %d, expected: %d. Setting FAILED status for Run: %s",
			len(pods), run.Spec.PodCount, run.Name)
		stateToSet = common.Failed
	}
	return stateToSet
}

func calculateRunStateFromPods(pods []*corev1.Pod, runName string) common.RunState {
	statuses := map[corev1.PodPhase]int{
		corev1.PodPending:   0,
		corev1.PodUnknown:   0,
		corev1.PodRunning:   0,
		corev1.PodSucceeded: 0,
	}

	for _, pod := range pods {
		podPhase := pod.Status.Phase
		if podPhase == corev1.PodFailed {
			log.Printf("Run %s failed! Reason: pod Failed: %s", runName, pod.Status.Message)
			return common.Failed
		}
		statuses[podPhase] = statuses[podPhase] + 1
	}

	if statuses[corev1.PodPending] > 0 || statuses[corev1.PodUnknown] > 0 {
		return common.Queued
	}
	if statuses[corev1.PodSucceeded] == len(pods) {
		return common.Complete
	}
	return common.Running
}

// enqueueRun takes a Foo resource and converts it into a namespace/name
// string which is then put onto the work queue. This method should *not* be
// passed resources of any type other than Foo.
func (c *Controller) enqueueRun(obj interface{}) {
	var key string
	var err error
	if key, err = cache.MetaNamespaceKeyFunc(obj); err != nil {
		runtime.HandleError(err)
		return
	}
	c.workqueue.AddRateLimited(key)
}

// handleObject will take an instance of the watched resource (Pod) and attempt to find the Run resource that 'owns' it.
// It then enqueues that Run resource to be processed.
// If the Run object can not be found, it will simply be skipped.
func (c *Controller) handleObject(obj interface{}) {
	p, ok := obj.(*corev1.Pod)
	if !ok {
		runtime.HandleError(fmt.Errorf("error decoding object, invalid type"))
		return
	}
	log.Printf("Pod change detected. Pod: %v", p.Name)

	if runName, ok := p.Labels["runName"]; ok {
		run, err := c.runclientset.AggregatorV1().Runs(p.Namespace).Get(runName, metav1.GetOptions{})
		if err != nil {
			runtime.HandleError(fmt.Errorf("can not found Run: %s for Pod: %s. Error: %v", runName, p.Name, err))
			return
		}

		log.Printf("Run found: %s for Pod: %s", run.Name, p.Name)

		c.enqueueRun(run)
		return
	}
}
