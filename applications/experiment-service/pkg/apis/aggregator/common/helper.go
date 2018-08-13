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

package common

import (
	"fmt"
	"strings"
)

func RunFieldLabelConversion(label, value string) (string, string, error) {
	if strings.HasPrefix(label, "spec.metrics.") {
		return label, value, nil
	}

	switch label {
	case "metadata.name",
		"metadata.namespace",
		"spec.metrics",
		"spec.state":
		return label, value, nil
	default:
		return "", "", fmt.Errorf("run field label not supported: %s", label)
	}
}
