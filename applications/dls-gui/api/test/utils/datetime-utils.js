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

const expect = require('chai').expect;
const datetimeUtils = require('../../src/utils/datetime-utils');

describe('Utils ', function () {

  let str;

  beforeEach(function () {
    str = '2018-05-23T11:50:27Z';
  });

  describe('parseStringToUTC', function () {
    it('should return UTC string if str valid', function () {
      const expectedResult = 'Wed, 23 May 2018 11:50:27 GMT';
      const result = datetimeUtils.parseStringToUTC(str);
      expect(result).to.equal(expectedResult);
    });

    it('should return the same object if cannot parse str', function () {
      const expectedResult = '';
      str = '';
      const result = datetimeUtils.parseStringToUTC(str);
      expect(result).to.equal(expectedResult);
    });
  });
});
