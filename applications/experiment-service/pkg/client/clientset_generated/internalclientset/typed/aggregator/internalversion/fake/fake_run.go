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
*/package fake

import (
	aggregator "github.com/nervanasystems/carbon/applications/experiment-service/pkg/apis/aggregator"
	v1 "k8s.io/apimachinery/pkg/apis/meta/v1"
	labels "k8s.io/apimachinery/pkg/labels"
	schema "k8s.io/apimachinery/pkg/runtime/schema"
	types "k8s.io/apimachinery/pkg/types"
	watch "k8s.io/apimachinery/pkg/watch"
	testing "k8s.io/client-go/testing"
)

// FakeRuns implements RunInterface
type FakeRuns struct {
	Fake *FakeAggregator
	ns   string
}

var runsResource = schema.GroupVersionResource{Group: "aggregator.aipg.intel.com", Version: "", Resource: "runs"}

var runsKind = schema.GroupVersionKind{Group: "aggregator.aipg.intel.com", Version: "", Kind: "Run"}

// Get takes name of the run, and returns the corresponding run object, and an error if there is any.
func (c *FakeRuns) Get(name string, options v1.GetOptions) (result *aggregator.Run, err error) {
	obj, err := c.Fake.
		Invokes(testing.NewGetAction(runsResource, c.ns, name), &aggregator.Run{})

	if obj == nil {
		return nil, err
	}
	return obj.(*aggregator.Run), err
}

// List takes label and field selectors, and returns the list of Runs that match those selectors.
func (c *FakeRuns) List(opts v1.ListOptions) (result *aggregator.RunList, err error) {
	obj, err := c.Fake.
		Invokes(testing.NewListAction(runsResource, runsKind, c.ns, opts), &aggregator.RunList{})

	if obj == nil {
		return nil, err
	}

	label, _, _ := testing.ExtractFromListOptions(opts)
	if label == nil {
		label = labels.Everything()
	}
	list := &aggregator.RunList{}
	for _, item := range obj.(*aggregator.RunList).Items {
		if label.Matches(labels.Set(item.Labels)) {
			list.Items = append(list.Items, item)
		}
	}
	return list, err
}

// Watch returns a watch.Interface that watches the requested runs.
func (c *FakeRuns) Watch(opts v1.ListOptions) (watch.Interface, error) {
	return c.Fake.
		InvokesWatch(testing.NewWatchAction(runsResource, c.ns, opts))

}

// Create takes the representation of a run and creates it.  Returns the server's representation of the run, and an error, if there is any.
func (c *FakeRuns) Create(run *aggregator.Run) (result *aggregator.Run, err error) {
	obj, err := c.Fake.
		Invokes(testing.NewCreateAction(runsResource, c.ns, run), &aggregator.Run{})

	if obj == nil {
		return nil, err
	}
	return obj.(*aggregator.Run), err
}

// Update takes the representation of a run and updates it. Returns the server's representation of the run, and an error, if there is any.
func (c *FakeRuns) Update(run *aggregator.Run) (result *aggregator.Run, err error) {
	obj, err := c.Fake.
		Invokes(testing.NewUpdateAction(runsResource, c.ns, run), &aggregator.Run{})

	if obj == nil {
		return nil, err
	}
	return obj.(*aggregator.Run), err
}

// UpdateStatus was generated because the type contains a Status member.
// Add a +genclient:noStatus comment above the type to avoid generating UpdateStatus().
func (c *FakeRuns) UpdateStatus(run *aggregator.Run) (*aggregator.Run, error) {
	obj, err := c.Fake.
		Invokes(testing.NewUpdateSubresourceAction(runsResource, "status", c.ns, run), &aggregator.Run{})

	if obj == nil {
		return nil, err
	}
	return obj.(*aggregator.Run), err
}

// Delete takes name of the run and deletes it. Returns an error if one occurs.
func (c *FakeRuns) Delete(name string, options *v1.DeleteOptions) error {
	_, err := c.Fake.
		Invokes(testing.NewDeleteAction(runsResource, c.ns, name), &aggregator.Run{})

	return err
}

// DeleteCollection deletes a collection of objects.
func (c *FakeRuns) DeleteCollection(options *v1.DeleteOptions, listOptions v1.ListOptions) error {
	action := testing.NewDeleteCollectionAction(runsResource, c.ns, listOptions)

	_, err := c.Fake.Invokes(action, &aggregator.RunList{})
	return err
}

// Patch applies the patch and returns the patched run.
func (c *FakeRuns) Patch(name string, pt types.PatchType, data []byte, subresources ...string) (result *aggregator.Run, err error) {
	obj, err := c.Fake.
		Invokes(testing.NewPatchSubresourceAction(runsResource, c.ns, name, data, subresources...), &aggregator.Run{})

	if obj == nil {
		return nil, err
	}
	return obj.(*aggregator.Run), err
}
