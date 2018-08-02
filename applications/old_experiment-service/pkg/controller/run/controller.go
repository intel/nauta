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
	"encoding/json"
	"errors"
	"fmt"
	"log"

	"github.com/kubernetes-incubator/apiserver-builder/pkg/builders"
	core_v1 "k8s.io/api/core/v1"
	meta_v1 "k8s.io/apimachinery/pkg/apis/meta/v1"
	"k8s.io/apimachinery/pkg/types"
	listers_v1 "k8s.io/client-go/listers/core/v1"

	"github.com/nervanasystems/carbon/applications/experiment-service/pkg/apis/aggregator/common"
	"github.com/nervanasystems/carbon/applications/experiment-service/pkg/apis/aggregator/v1"
	client_run "github.com/nervanasystems/carbon/applications/experiment-service/pkg/client/clientset_generated/clientset/typed/aggregator/v1"
	listers_run "github.com/nervanasystems/carbon/applications/experiment-service/pkg/client/listers_generated/aggregator/v1"
	"github.com/nervanasystems/carbon/applications/experiment-service/pkg/controller/sharedinformers"
)

// podLister indexes properties about Pods - it is class package variable, because is needed for tests purpose
var podLister listers_v1.PodLister

// +controller:group=aggregator,version=v1,kind=Run,resource=runs
type RunControllerImpl struct {
	builders.DefaultControllerFns

	// runLister indexes properties about Run
	runLister listers_run.RunLister

	runClient client_run.AggregatorV1Interface
}

// Init initializes the controller and is called by the generated code
// Register watches for additional resource types here.
func (c *RunControllerImpl) Init(arguments sharedinformers.ControllerInitArguments) {
	pi := arguments.GetSharedInformers().KubernetesFactory.Core().V1().Pods()
	podLister = pi.Lister()

	// For watching Pods
	arguments.Watch("RunPod", pi.Informer(), c.getReconcileKey)

	// Use the runLister for indexing runs labels
	c.runLister = arguments.GetSharedInformers().Factory.Aggregator().V1().Runs().Lister()

	var err error
	c.runClient, err = client_run.NewForConfig(arguments.GetRestConfig())
	if err != nil {
		log.Fatalln("Client not created sucessfully:", err)
	}
}

// Reconcile handles enqueued message
// Create and Update events for RUN object are also handled. Delete hook has to be added manually.
func (c *RunControllerImpl) Reconcile(run *v1.Run) error {
	log.Printf("Processing Run: %s. State: %v", run.Name, run.Spec.State)

	selector, err := meta_v1.LabelSelectorAsSelector(&run.Spec.PodSelector)
	if err != nil {
		log.Printf("Run: %s. Convert LabelSelector to Selector Fail: %v", run.Name, err)
		return err
	}

	pods, err := podLister.Pods(run.Namespace).List(selector)
	if err != nil {
		log.Printf("Run: %s. List pod error: %v", run.Name, err)
		return err
	}

	if run.Spec.State == common.Complete || run.Spec.State == common.Failed || run.Spec.State == common.Cancelled {
		log.Printf("SKIPPING. Run: %s already processed. Final status %v", run.Name, run.Spec.State)
		return nil
	}

	if run.Spec.State == "" && len(pods) < run.Spec.PodCount {
		log.Printf("SKIPPING. Run: %s NOT READY to start yet. Not enough pods. Required %d, currently: %d",
			run.Name, run.Spec.PodCount, len(pods))
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

func (c *RunControllerImpl) updateState(run *v1.Run, stateToSet common.RunState, pods []*core_v1.Pod) error {
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
			log.Printf("Run %s prepare patch error: %v", run.Name, errMarshal)
			return errMarshal
		}

		_, err := c.runClient.Runs(run.Namespace).Patch(run.Name, types.JSONPatchType, patchBytes)
		if err != nil {
			errMsg := fmt.Sprintf("Run %s patch FAILED! Error: %v", run.Name, err)
			log.Printf(errMsg)
			return errors.New(errMsg)
		}
		run.Spec.State = stateToSet
		return nil
	}

	log.Printf("Run: %s state (%v) not changed. Update no required", run.Name, run.Spec.State)
	return nil
}

func calculateRunState(run *v1.Run, pods []*core_v1.Pod) common.RunState {
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

func calculateRunStateFromPods(pods []*core_v1.Pod, runName string) common.RunState {
	statuses := map[core_v1.PodPhase]int{
		core_v1.PodPending:   0,
		core_v1.PodUnknown:   0,
		core_v1.PodRunning:   0,
		core_v1.PodSucceeded: 0,
	}

	for _, pod := range pods {
		podPhase := pod.Status.Phase
		if podPhase == core_v1.PodFailed {
			log.Printf("Run %s failed! Reason: pod Failed: %s", runName, pod.Status.Message)
			return common.Failed
		}
		statuses[podPhase] = statuses[podPhase] + 1
	}

	if statuses[core_v1.PodPending] > 0 || statuses[core_v1.PodUnknown] > 0 {
		return common.Queued
	}
	if statuses[core_v1.PodSucceeded] == len(pods) {
		return common.Complete
	}
	return common.Running
}

// this method is executed just before the Reconcile method to lookup the Run object.
func (c *RunControllerImpl) Get(namespace, name string) (*v1.Run, error) {
	return c.runClient.Runs(namespace).Get(name, meta_v1.GetOptions{})
}

// takes an instance of the watched resource (Pod) and returns a key for the reconciled resource type (Run) to enqueue
func (c *RunControllerImpl) getReconcileKey(i interface{}) (string, error) {
	p, _ := i.(*core_v1.Pod)
	log.Printf("Pod change detected. Pod: %v", p.Name)

	if label, ok := p.Labels["runName"]; ok {
		log.Printf("Run found: %s for Pod: %s", label, p.Name)
		return p.Namespace + "/" + label, nil
	}

	// Not owned
	return "", nil
}
