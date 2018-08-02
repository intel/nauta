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

package v1

import (
	metav1 "k8s.io/apimachinery/pkg/apis/meta/v1"

	"github.com/nervanasystems/carbon/applications/experiment-service/pkg/apis/aggregator/common"
)

// +genclient
// +k8s:deepcopy-gen:interfaces=k8s.io/apimachinery/pkg/runtime.Object

type Run struct {
	metav1.TypeMeta   `json:",inline"`
	metav1.ObjectMeta `json:"metadata,omitempty"`

	Spec   RunSpec   `json:"spec,omitempty"`
	Status RunStatus `json:"status,omitempty"`
}

// +k8s:deepcopy-gen:interfaces=k8s.io/apimachinery/pkg/runtime.Object

type RunList struct {
	metav1.TypeMeta `json:",inline"`
	metav1.ListMeta `json:"metadata,omitempty"`
	Items           []Run `json:"items"`
}

type RunSpec struct {
	ExperimentName string               `json:"experiment-name,omitempty"`
	PodSelector    metav1.LabelSelector `json:"pod-selector,omitempty"`
	PodCount       int                  `json:"pod-count,omitempty"`
	Parameters     []string             `json:"parameters,omitempty"`
	Metrics        map[string]string    `json:"metrics,omitempty"`
	State          common.RunState      `json:"state,omitempty"`
}

// RunStatus defines the observed state of Run
type RunStatus struct {
	// TODO common.RunState state should be set here?
}
