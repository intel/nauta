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
const sinon = require('sinon');
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

  describe('calculateTimeDifferenceFromDateString', function () {
    it('should 0 if start date is empty', function () {
      const expectedResult = 0;
      const result = datetimeUtils.calculateTimeDifferenceFromDateString();
      expect(result).to.equal(expectedResult);
    });

    it('should return difference if start and end times defined', function () {
      const startDate = '2018-08-24T06:42:10Z';
      const endDate = '2018-08-24T06:43:10Z';
      const expectedResult = 60000;
      const result = datetimeUtils.calculateTimeDifferenceFromDateString(startDate, endDate);
      expect(result).to.equal(expectedResult);
    });

    it('should return difference between start and current time if only start date defined', function () {
      const startDate = '2018-08-24T06:42:10Z';
      const endDate = '2018-08-24T06:43:10Z';
      const clock = sinon.useFakeTimers(new Date(endDate).getTime());
      const expectedResult = 60000;
      const result = datetimeUtils.calculateTimeDifferenceFromDateString(startDate);
      expect(result).to.equal(expectedResult);
      clock.restore();
    });
  });
});
