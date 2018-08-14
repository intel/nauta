package main

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
