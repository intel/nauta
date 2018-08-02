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
*/package v1

import (
	v1 "github.com/nervanasystems/carbon/applications/experiment-service/pkg/apis/aggregator/v1"
	scheme "github.com/nervanasystems/carbon/applications/experiment-service/pkg/client/clientset_generated/clientset/scheme"
	meta_v1 "k8s.io/apimachinery/pkg/apis/meta/v1"
	types "k8s.io/apimachinery/pkg/types"
	watch "k8s.io/apimachinery/pkg/watch"
	rest "k8s.io/client-go/rest"
)

// RunsGetter has a method to return a RunInterface.
// A group's client should implement this interface.
type RunsGetter interface {
	Runs(namespace string) RunInterface
}

// RunInterface has methods to work with Run resources.
type RunInterface interface {
	Create(*v1.Run) (*v1.Run, error)
	Update(*v1.Run) (*v1.Run, error)
	UpdateStatus(*v1.Run) (*v1.Run, error)
	Delete(name string, options *meta_v1.DeleteOptions) error
	DeleteCollection(options *meta_v1.DeleteOptions, listOptions meta_v1.ListOptions) error
	Get(name string, options meta_v1.GetOptions) (*v1.Run, error)
	List(opts meta_v1.ListOptions) (*v1.RunList, error)
	Watch(opts meta_v1.ListOptions) (watch.Interface, error)
	Patch(name string, pt types.PatchType, data []byte, subresources ...string) (result *v1.Run, err error)
	RunExpansion
}

// runs implements RunInterface
type runs struct {
	client rest.Interface
	ns     string
}

// newRuns returns a Runs
func newRuns(c *AggregatorV1Client, namespace string) *runs {
	return &runs{
		client: c.RESTClient(),
		ns:     namespace,
	}
}

// Get takes name of the run, and returns the corresponding run object, and an error if there is any.
func (c *runs) Get(name string, options meta_v1.GetOptions) (result *v1.Run, err error) {
	result = &v1.Run{}
	err = c.client.Get().
		Namespace(c.ns).
		Resource("runs").
		Name(name).
		VersionedParams(&options, scheme.ParameterCodec).
		Do().
		Into(result)
	return
}

// List takes label and field selectors, and returns the list of Runs that match those selectors.
func (c *runs) List(opts meta_v1.ListOptions) (result *v1.RunList, err error) {
	result = &v1.RunList{}
	err = c.client.Get().
		Namespace(c.ns).
		Resource("runs").
		VersionedParams(&opts, scheme.ParameterCodec).
		Do().
		Into(result)
	return
}

// Watch returns a watch.Interface that watches the requested runs.
func (c *runs) Watch(opts meta_v1.ListOptions) (watch.Interface, error) {
	opts.Watch = true
	return c.client.Get().
		Namespace(c.ns).
		Resource("runs").
		VersionedParams(&opts, scheme.ParameterCodec).
		Watch()
}

// Create takes the representation of a run and creates it.  Returns the server's representation of the run, and an error, if there is any.
func (c *runs) Create(run *v1.Run) (result *v1.Run, err error) {
	result = &v1.Run{}
	err = c.client.Post().
		Namespace(c.ns).
		Resource("runs").
		Body(run).
		Do().
		Into(result)
	return
}

// Update takes the representation of a run and updates it. Returns the server's representation of the run, and an error, if there is any.
func (c *runs) Update(run *v1.Run) (result *v1.Run, err error) {
	result = &v1.Run{}
	err = c.client.Put().
		Namespace(c.ns).
		Resource("runs").
		Name(run.Name).
		Body(run).
		Do().
		Into(result)
	return
}

// UpdateStatus was generated because the type contains a Status member.
// Add a +genclient:noStatus comment above the type to avoid generating UpdateStatus().

func (c *runs) UpdateStatus(run *v1.Run) (result *v1.Run, err error) {
	result = &v1.Run{}
	err = c.client.Put().
		Namespace(c.ns).
		Resource("runs").
		Name(run.Name).
		SubResource("status").
		Body(run).
		Do().
		Into(result)
	return
}

// Delete takes name of the run and deletes it. Returns an error if one occurs.
func (c *runs) Delete(name string, options *meta_v1.DeleteOptions) error {
	return c.client.Delete().
		Namespace(c.ns).
		Resource("runs").
		Name(name).
		Body(options).
		Do().
		Error()
}

// DeleteCollection deletes a collection of objects.
func (c *runs) DeleteCollection(options *meta_v1.DeleteOptions, listOptions meta_v1.ListOptions) error {
	return c.client.Delete().
		Namespace(c.ns).
		Resource("runs").
		VersionedParams(&listOptions, scheme.ParameterCodec).
		Body(options).
		Do().
		Error()
}

// Patch applies the patch and returns the patched run.
func (c *runs) Patch(name string, pt types.PatchType, data []byte, subresources ...string) (result *v1.Run, err error) {
	result = &v1.Run{}
	err = c.client.Patch(pt).
		Namespace(c.ns).
		Resource("runs").
		SubResource(subresources...).
		Name(name).
		Body(data).
		Do().
		Into(result)
	return
}
