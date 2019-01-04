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
const expect = require('chai').expect;
const errorHandler = require('../../src/utils/error-handler');

describe('Utils ', function () {

  describe('error-handler', function () {
    it('should return error object', function () {
      const status = 400;
      const message = 'message';
      const result = errorHandler(status, message);
      expect(result.status).to.equal(status);
      expect(result.message).to.equal(message);
    });
  });
});
