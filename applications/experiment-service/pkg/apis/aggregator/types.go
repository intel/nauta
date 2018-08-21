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

package aggregator

import (
	metav1 "k8s.io/apimachinery/pkg/apis/meta/v1"

	"github.com/nervanasystems/carbon/applications/experiment-service/pkg/apis/aggregator/common"
)

// +genclient
// +k8s:deepcopy-gen:interfaces=k8s.io/apimachinery/pkg/runtime.Object

type Run struct {
	metav1.TypeMeta
	metav1.ObjectMeta

	Spec   RunSpec
	Status RunStatus
}

// +k8s:deepcopy-gen:interfaces=k8s.io/apimachinery/pkg/runtime.Object

type RunList struct {
	metav1.TypeMeta
	metav1.ListMeta
	Items []Run
}

type RunSpec struct {
	ExperimentName string
	PodSelector    metav1.LabelSelector
	PodCount       int
	Parameters     []string
	Metrics        map[string]string
	State          common.RunState
	StartTime      metav1.Time
	EndTime        metav1.Time
}

type RunStatus struct {
}
