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

package main

import (
	"flag"
	"log"

	controllerlib "github.com/kubernetes-incubator/apiserver-builder/pkg/controller"

	"github.com/nervanasystems/carbon/applications/test-exp-service/pkg/controller"
)

var kubeconfig = flag.String("kubeconfig", "", "path to kubeconfig")

func main() {
	flag.Parse()
	config, err := controllerlib.GetConfig(*kubeconfig)
	if err != nil {
		log.Fatalf("Could not create Config for talking to the apiserver: %v", err)
	}

	controllers, _ := controller.GetAllControllers(config)
	controllerlib.StartControllerManager(controllers...)

	// Blockforever
	select {}
}
