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

package run

import (
	"fmt"
	"github.com/golang/glog"
	"k8s.io/apimachinery/pkg/fields"
	"k8s.io/apimachinery/pkg/labels"
	"k8s.io/apimachinery/pkg/runtime"
	"k8s.io/apimachinery/pkg/util/validation/field"
	genericapirequest "k8s.io/apiserver/pkg/endpoints/request"
	"k8s.io/apiserver/pkg/registry/generic"
	"k8s.io/apiserver/pkg/storage"
	"k8s.io/apiserver/pkg/storage/names"

	"github.com/nervanasystems/carbon/applications/experiment-service/pkg/apis/aggregator"
)

// NewStrategy creates and returns a runStrategy instance
func NewStrategy(typer runtime.ObjectTyper) runStrategy {
	return runStrategy{typer, names.SimpleNameGenerator}
}

// GetAttrs returns labels.Set, fields.Set, the presence of Initializers if any
// and error in case the given runtime.Object is not a Run
func GetAttrs(obj runtime.Object) (labels.Set, fields.Set, bool, error) {
	apiserver, ok := obj.(*aggregator.Run)
	if !ok {
		return nil, nil, false, fmt.Errorf("given object is not a Run")
	}
	return labels.Set(apiserver.ObjectMeta.Labels), selectableFieldsSet(apiserver), apiserver.Initializers != nil, nil
}

// MatchRun is the filter used by the generic etcd backend to watch events
// from etcd to clients of the apiserver only interested in specific labels/fields.
func MatchRun(label labels.Selector, field fields.Selector) storage.SelectionPredicate {
	return storage.SelectionPredicate{
		Label:    label,
		Field:    field,
		GetAttrs: GetAttrs,
	}
}

// SelectableFields returns a field set that represents the object.
func selectableFieldsSet(run *aggregator.Run) fields.Set {
	selectableFields := generic.ObjectMetaFieldsSet(&run.ObjectMeta, true)

	// filtering through metrics is switched off since we are not going to use it and may have a big impact on performance during filtering
	// selectableFields = addMetricsToSelectableFields(run.Spec.Metrics, selectableFields)
	selectableFields["spec.state"] = string(run.Spec.State)
	return selectableFields
}

func addMetricsToSelectableFields(metrics map[string]string, selectableFields fields.Set) fields.Set {
	for k, value := range metrics {
		selectableFields[fmt.Sprintf("spec.metrics.%s", k)] = value
	}
	return selectableFields
}

type runStrategy struct {
	runtime.ObjectTyper
	names.NameGenerator
}

func (runStrategy) NamespaceScoped() bool {
	return true
}

func (runStrategy) PrepareForCreate(ctx genericapirequest.Context, obj runtime.Object) {
	updateRunLabels(obj)
}

func (runStrategy) PrepareForUpdate(ctx genericapirequest.Context, obj, old runtime.Object) {
	updateRunLabels(obj)
}

func updateRunLabels(obj runtime.Object) {
	run, ok := obj.(*aggregator.Run)
	if !ok {
		glog.Errorf("can not update labels for run! Incorrect obj type: %v", obj.GetObjectKind())
		return
	}

	if run.Labels == nil {
		run.Labels = make(map[string]string)
	}
	run.Labels["name"] = run.Name
	run.Labels["namespace"] = run.Namespace
}

func (runStrategy) Validate(ctx genericapirequest.Context, obj runtime.Object) field.ErrorList {
	return field.ErrorList{}
}

func (runStrategy) AllowCreateOnUpdate() bool {
	return false
}

func (runStrategy) AllowUnconditionalUpdate() bool {
	return false
}

func (runStrategy) Canonicalize(obj runtime.Object) {
}

func (runStrategy) ValidateUpdate(ctx genericapirequest.Context, obj, old runtime.Object) field.ErrorList {
	return field.ErrorList{}
}
