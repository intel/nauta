/**
 * Copyright (c) 2019 Intel Corporation
 *
 * Licensed under the Apache License, Version 2.0 (the "License");
 * you may not use this file except in compliance with the License.
 * You may obtain a copy of the License at
 *
 *      http://www.apache.org/licenses/LICENSE-2.0
 *
 * Unless required by applicable law or agreed to in writing, software
 * distributed under the License is distributed on an "AS IS" BASIS,
 * WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
 * See the License for the specific language governing permissions and
 * limitations under the License.
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
