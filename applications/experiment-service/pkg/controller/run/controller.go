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
	"log"

	"github.com/kubernetes-incubator/apiserver-builder/pkg/builders"

	"github.com/nervanasystems/carbon/applications/experiment-service/pkg/apis/aggregator/common"
	"github.com/nervanasystems/carbon/applications/experiment-service/pkg/apis/aggregator/v1"
	v1client "github.com/nervanasystems/carbon/applications/experiment-service/pkg/client/clientset_generated/clientset/typed/aggregator/v1"
	listers "github.com/nervanasystems/carbon/applications/experiment-service/pkg/client/listers_generated/aggregator/v1"
	"github.com/nervanasystems/carbon/applications/experiment-service/pkg/controller/sharedinformers"
	v1core "k8s.io/api/core/v1"
	metav1 "k8s.io/apimachinery/pkg/apis/meta/v1"
	v1listers "k8s.io/client-go/listers/core/v1"
)

// +controller:group=aggregator,version=v1,kind=Run,resource=runs
type RunControllerImpl struct {
	builders.DefaultControllerFns

	// lister indexes properties about Run
	lister listers.RunLister

	// lister indexes properties about Pods
	podLister v1listers.PodLister

	runClient *v1client.AggregatorV1Client
}

// Init initializes the controller and is called by the generated code
// Register watches for additional resource types here.
func (c *RunControllerImpl) Init(arguments sharedinformers.ControllerInitArguments) {
	pi := arguments.GetSharedInformers().KubernetesFactory.Core().V1().Pods()
	c.podLister = pi.Lister()

	// For watching Pods
	arguments.Watch("RunPod", pi.Informer(), c.getReconcileKey)
	arguments.GetRestConfig()

	// Use the lister for indexing runs labels
	c.lister = arguments.GetSharedInformers().Factory.Aggregator().V1().Runs().Lister()

	var err error
	c.runClient, err = v1client.NewForConfig(arguments.GetRestConfig())
	if err != nil {
		log.Fatalln("Client not created sucessfully:", err)
	}
}

// Reconcile handles enqueued messages
func (c *RunControllerImpl) Reconcile(run *v1.Run) error {
	log.Printf("Processing Run: %s", run.Name)

	if run.Spec.State == common.Complete || run.Spec.State == common.Failed || run.Spec.State == common.Cancelled {
		log.Printf("Run object: %s already processed. Final status %v", run.Name, run.Spec.State)
		return nil
	}

	if run.Spec.State == "" {
		log.Printf("Run object: %s CREATE flow. Changing state to %v", run.Name, common.Queued)
		run.Spec.State = common.Queued
		_, err := c.runClient.Runs(run.Namespace).Update(run)
		if err != nil {
			log.Printf("Run %s update after Create - FALED! %v", run.Name, err)
		}
		return err
	}

	selector, err := metav1.LabelSelectorAsSelector(&run.Spec.PodSelector)
	if err != nil {
		log.Printf("Run: %s. Convert LabelSelector to Selector Fail: %v", run.Name, err)
		return err
	}

	pods, err := c.podLister.Pods(run.Namespace).List(selector)
	if err != nil {
		log.Printf("Run: %s. List pod error: %v", run.Name, err)
		return err
	}

	// TODO implement Run.Spec.PodCount - check '4.3.1.3.1. State FSM' section in doc

	if len(pods) > 0 {
		newState := calculateRunStatus(pods, run.Name)
		run.Spec.State = newState
		log.Printf("Run %s. New calculated state: %v", run.Name, newState)
	} else {
		log.Printf("No Pods found. Setting FAILED status for Run: %s", run.Name)
		run.Spec.State = common.Failed
	}

	// TODO move Run.Spec.State to Run.Status and use UpdateStatus method
	_, err = c.runClient.Runs(run.Namespace).Update(run)
	if err != nil {
		log.Printf("Run %s update - FALED! %v", run.Name, err)
		return err
	}
	return nil
}

func calculateRunStatus(pods []*v1core.Pod, runName string) common.RunState {
	statuses := map[v1core.PodPhase]int{
		v1core.PodPending:   0,
		v1core.PodUnknown:   0,
		v1core.PodRunning:   0,
		v1core.PodSucceeded: 0,
	}

	for _, pod := range pods {
		podPhase := pod.Status.Phase
		if podPhase == v1core.PodFailed {
			log.Printf("Run %s failed! Reason: pod Failed: %s", runName, pod.Status.Message)
			return common.Failed
		}
		statuses[podPhase] = statuses[podPhase] + 1
	}

	if statuses[v1core.PodPending] > 0 || statuses[v1core.PodUnknown] > 0 {
		return common.Queued
	}
	if statuses[v1core.PodSucceeded] == len(pods) {
		return common.Complete
	}
	return common.Running
}

// this method is executed just before the Reconcile method to lookup the Run object.
func (c *RunControllerImpl) Get(namespace, name string) (*v1.Run, error) {
	return c.lister.Runs(namespace).Get(name)
}

// takes an instance of the watched resource (Pod) and returns a key for the reconciled resource type (Run) to enqueue
func (c *RunControllerImpl) getReconcileKey(i interface{}) (string, error) {
	p, _ := i.(*v1core.Pod)
	log.Printf("Pod change detected. Pod: %v", p.Name)

	if label, ok := p.Labels["runName"]; ok {
		log.Printf("Run found: %s for Pod: %s", label, p.Name)
		return p.Namespace + "/" + label, nil
	}

	// Not owned
	return "", nil
}
