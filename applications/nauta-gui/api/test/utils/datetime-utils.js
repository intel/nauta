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
