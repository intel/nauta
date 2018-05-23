/**
 * INTEL CONFIDENTIAL
 * Copyright (c) 2018 Intel Corporation
 *
 * The source code contained or described herein and all documents related to
 * the source code ("Material") are owned by Intel Corporation or its suppliers
 * or licensors. Title to the Material remains with Intel Corporation or its
 * suppliers and licensors. The Material contains trade secrets and proprietary
 * and confidential information of Intel or its suppliers and licensors. The
 * Material is protected by worldwide copyright and trade secret laws and treaty
 * provisions. No part of the Material may be used, copied, reproduced, modified,
 * published, uploaded, posted, transmitted, distributed, or disclosed in any way
 * without Intel's prior express written permission.
 *
 * No license under any patent, copyright, trade secret or other intellectual
 * property right is granted to or conferred upon you by disclosure or delivery
 * of the Materials, either expressly, by implication, inducement, estoppel or
 * otherwise. Any license under such intellectual property rights must be express
 * and approved by Intel in writing.
 */

export function testAction (action, payload, state, expectedMutations, expectedActions, done) {
  let mutationsCount = 0;
  let actionsCount = 0;

  const commit = function (type, payload) {
    const mutation = expectedMutations[mutationsCount];
    try {
      expect(type).to.equal(mutation.type);
      if (payload) {
        expect(payload).to.deep.equal(mutation.payload);
      }
    } catch (error) {
      done(error);
    }

    mutationsCount++;
    if (mutationsCount >= expectedMutations.length) {
      done();
    }
  };

  const dispatch = function (type, payload) {
    const action = expectedActions[actionsCount];
    try {
      expect(type).to.equal(action.type);
      if (payload) {
        expect(payload).to.deep.equal(action.payload);
      }
    } catch (error) {
      done(error);
    }

    actionsCount++;
    if (actionsCount >= expectedActions.length) {
      done();
    }
  };

  action({commit, dispatch, state}, payload);

  if (expectedMutations.length === 0 && expectedActions.length === 0) {
    expect(mutationsCount).to.equal(0);
    expect(actionsCount).to.equal(0);
    done();
  }
}
