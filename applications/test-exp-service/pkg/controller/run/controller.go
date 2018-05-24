
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
	"log"

	"github.com/kubernetes-incubator/apiserver-builder/pkg/builders"

	"github.com/nervanasystems/carbon/applications/test-exp-service/pkg/apis/aggregator/v1"
	"github.com/nervanasystems/carbon/applications/test-exp-service/pkg/controller/sharedinformers"
	listers "github.com/nervanasystems/carbon/applications/test-exp-service/pkg/client/listers_generated/aggregator/v1"
)

// +controller:group=aggregator,version=v1,kind=Run,resource=runs
type RunControllerImpl struct {
	builders.DefaultControllerFns

	// lister indexes properties about Run
	lister listers.RunLister
}

// Init initializes the controller and is called by the generated code
// Register watches for additional resource types here.
func (c *RunControllerImpl) Init(arguments sharedinformers.ControllerInitArguments) {
	// Use the lister for indexing runs labels
	c.lister = arguments.GetSharedInformers().Factory.Aggregator().V1().Runs().Lister()
}

// Reconcile handles enqueued messages
func (c *RunControllerImpl) Reconcile(u *v1.Run) error {
	// Implement controller logic here
	log.Printf("Running reconcile Run for %s\n", u.Name)
	return nil
}

func (c *RunControllerImpl) Get(namespace, name string) (*v1.Run, error) {
	return c.lister.Runs(namespace).Get(name)
}
