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
*/package internalversion

import (
	"github.com/nervanasystems/carbon/applications/test-exp-service/pkg/client/clientset_generated/internalclientset/scheme"
	rest "k8s.io/client-go/rest"
)

type AggregatorInterface interface {
	RESTClient() rest.Interface
	RunsGetter
}

// AggregatorClient is used to interact with features provided by the aggregator.aipg.intel.com group.
type AggregatorClient struct {
	restClient rest.Interface
}

func (c *AggregatorClient) Runs(namespace string) RunInterface {
	return newRuns(c, namespace)
}

// NewForConfig creates a new AggregatorClient for the given config.
func NewForConfig(c *rest.Config) (*AggregatorClient, error) {
	config := *c
	if err := setConfigDefaults(&config); err != nil {
		return nil, err
	}
	client, err := rest.RESTClientFor(&config)
	if err != nil {
		return nil, err
	}
	return &AggregatorClient{client}, nil
}

// NewForConfigOrDie creates a new AggregatorClient for the given config and
// panics if there is an error in the config.
func NewForConfigOrDie(c *rest.Config) *AggregatorClient {
	client, err := NewForConfig(c)
	if err != nil {
		panic(err)
	}
	return client
}

// New creates a new AggregatorClient for the given RESTClient.
func New(c rest.Interface) *AggregatorClient {
	return &AggregatorClient{c}
}

func setConfigDefaults(config *rest.Config) error {
	g, err := scheme.Registry.Group("aggregator.aipg.intel.com")
	if err != nil {
		return err
	}

	config.APIPath = "/apis"
	if config.UserAgent == "" {
		config.UserAgent = rest.DefaultKubernetesUserAgent()
	}
	if config.GroupVersion == nil || config.GroupVersion.Group != g.GroupVersion.Group {
		gv := g.GroupVersion
		config.GroupVersion = &gv
	}
	config.NegotiatedSerializer = scheme.Codecs

	if config.QPS == 0 {
		config.QPS = 5
	}
	if config.Burst == 0 {
		config.Burst = 10
	}

	return nil
}

// RESTClient returns a RESTClient that is used to communicate
// with API server by this client implementation.
func (c *AggregatorClient) RESTClient() rest.Interface {
	if c == nil {
		return nil
	}
	return c.restClient
}
