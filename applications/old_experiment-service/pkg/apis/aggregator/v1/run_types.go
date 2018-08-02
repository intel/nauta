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

package v1

import (
	"log"

	"k8s.io/apimachinery/pkg/runtime"
	"k8s.io/apiserver/pkg/endpoints/request"

	metav1 "k8s.io/apimachinery/pkg/apis/meta/v1"
	"k8s.io/apimachinery/pkg/util/validation/field"

	"github.com/nervanasystems/carbon/applications/experiment-service/pkg/apis/aggregator"
	"github.com/nervanasystems/carbon/applications/experiment-service/pkg/apis/aggregator/common"
)

// +genclient
// +k8s:deepcopy-gen:interfaces=k8s.io/apimachinery/pkg/runtime.Object

// Run
// +k8s:openapi-gen=true
// +resource:path=runs,strategy=RunStrategy
type Run struct {
	metav1.TypeMeta   `json:",inline"`
	metav1.ObjectMeta `json:"metadata,omitempty"`

	Spec   RunSpec   `json:"spec,omitempty"`
	Status RunStatus `json:"status,omitempty"`
}

// RunSpec defines the desired state of Run
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

// Validate checks that an instance of Run is well formed
func (RunStrategy) Validate(ctx request.Context, obj runtime.Object) field.ErrorList {
	o := obj.(*aggregator.Run)
	log.Printf("Validating fields for Run %s\n", o.Name)
	errors := field.ErrorList{}
	// perform validation here and add to errors using field.Invalid
	return errors
}

// DefaultingFunction sets default Run field values
func (RunSchemeFns) DefaultingFunction(o interface{}) {
	// set default field values here
	// obj := o.(*Run)
	//log.Printf("Defaulting fields for Run %s\n", obj.Name)
}
