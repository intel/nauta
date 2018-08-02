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
	"fmt"
	"io"
	"net"

	"github.com/spf13/cobra"

	"github.com/nervanasystems/carbon/applications/experiment-service/pkg/apis/aggregator/v1"
	"github.com/nervanasystems/carbon/applications/experiment-service/pkg/apiserver"
	clientset "github.com/nervanasystems/carbon/applications/experiment-service/pkg/client/clientset/internalversion"
	informers "github.com/nervanasystems/carbon/applications/experiment-service/pkg/client/informers/internalversion"
	utilerrors "k8s.io/apimachinery/pkg/util/errors"
	genericapiserver "k8s.io/apiserver/pkg/server"
	genericoptions "k8s.io/apiserver/pkg/server/options"
)

const defaultEtcdPathPrefix = "/registry/aggregator.aipg.intel.com"

type RunServerOptions struct {
	RecommendedOptions *genericoptions.RecommendedOptions
	StdOut io.Writer
	StdErr io.Writer
}

func NewRunServerOptions(out, errOut io.Writer) *RunServerOptions {
	recOptions := genericoptions.NewRecommendedOptions(defaultEtcdPathPrefix, apiserver.Codecs.LegacyCodec(v1.SchemeGroupVersion))
	recOptions.Etcd.StorageConfig.Paging = true

	o := &RunServerOptions{
		RecommendedOptions: recOptions,
		StdOut: out,
		StdErr: errOut,
	}

	return o
}

// NewCommandStartRunServer provides a CLI handler for starting the apiserver
func NewCommandStartRunServer(out, errOut io.Writer, stopCh <-chan struct{}) *cobra.Command {
	o := NewRunServerOptions(out, errOut)

	cmd := &cobra.Command{
		Short: "Launch a Run API server",
		Long:  "Launch a Run API server",
		RunE: func(c *cobra.Command, args []string) error {
			if err := o.Complete(); err != nil {
				return err
			}
			if err := o.Validate(args); err != nil {
				return err
			}
			if err := o.RunAggregatorServer(stopCh); err != nil {
				return err
			}
			return nil
		},
	}

	flags := cmd.Flags()
	o.RecommendedOptions.AddFlags(flags)
	return cmd
}

func (o RunServerOptions) Validate(args []string) error {
	var errors []error
	errors = append(errors, o.RecommendedOptions.Validate()...)
	return utilerrors.NewAggregate(errors)
}

func (o *RunServerOptions) Complete() error {
	return nil
}

func (o *RunServerOptions) Config() (*apiserver.Config, error) {
	// register admission plugins
	// banflunder.Register(o.Admission.Plugins)

	// TODO have a "real" external address
	if err := o.RecommendedOptions.SecureServing.MaybeDefaultWithSelfSignedCerts("localhost",
		nil, []net.IP{net.ParseIP("127.0.0.1")}); err != nil {
		return nil, fmt.Errorf("error creating self-signed certificates: %v", err)
	}

	serverConfig := genericapiserver.NewRecommendedConfig(apiserver.Codecs)
	if err := o.RecommendedOptions.ApplyTo(serverConfig, apiserver.Scheme); err != nil {
		return nil, err
	}

	client, err := clientset.NewForConfig(serverConfig.LoopbackClientConfig)
	if err != nil {
		return nil, err
	}
	informerFactory := informers.NewSharedInformerFactory(client, serverConfig.LoopbackClientConfig.Timeout)

	config := &apiserver.Config{
		GenericConfig:         serverConfig,
		SharedInformerFactory: informerFactory,
	}
	return config, nil
}

func (o RunServerOptions) RunAggregatorServer(stopCh <-chan struct{}) error {
	config, err := o.Config()
	if err != nil {
		return err
	}

	server, err := config.Complete().New()
	if err != nil {
		return err
	}

	server.GenericAPIServer.AddPostStartHook("start-run-server-informers", func(context genericapiserver.PostStartHookContext) error {
		config.GenericConfig.SharedInformerFactory.Start(context.StopCh)
		return nil
	})

	return server.GenericAPIServer.PrepareRun().Run(stopCh)
}
