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
	core_v1 "k8s.io/api/core/v1"
	meta_v1 "k8s.io/apimachinery/pkg/apis/meta/v1"

	run_v1 "github.com/nervanasystems/carbon/applications/experiment-service/pkg/apis/aggregator/v1"
)

func prepareRunningPod() *core_v1.Pod {
	return preparePod(core_v1.PodRunning)
}

func preparePod(podPhase core_v1.PodPhase) *core_v1.Pod {
	pod := core_v1.Pod{}
	pod.Name = "pod-1"
	pod.Namespace = "tst-namespace"
	pod.Labels = map[string]string{"runName": "instance-1", "app": "x"}
	pod.Status.Phase = podPhase
	return &pod
}

func prepareRun(podsNo int) *run_v1.Run {
	run := run_v1.Run{}
	run.Name = "instance-1"
	run.Namespace = "tst-namespace"
	run.Spec.State = ""
	run.Spec.PodCount = podsNo
	run.Spec.PodSelector = meta_v1.LabelSelector{
		MatchLabels: map[string]string{"app": "x"},
	}
	return &run
}
