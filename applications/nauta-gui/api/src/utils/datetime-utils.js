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
const moment = require('moment');

module.exports.parseStringToUTC = function (str) {
  const timestamp = Date.parse(str);
  const result = new Date(timestamp);
  return result == 'Invalid Date' ? str : result.toUTCString();
};

module.exports.calculateTimeDifferenceFromDateString = function (timeA, timeB) {
  if (!timeA) {
    return 0;
  }
  if (!timeB) {
    const timedateA = new Date(timeA);
    const currentTime = Date.now();
    return currentTime - timedateA;
  }
  const timedateA = new Date(timeA).getTime();
  const timedateB = new Date(timeB).getTime();
  return timedateB - timedateA;
};

module.exports.getLocaleStringForOffset = function (timeString, offset) {
  const serverOffset = new Date().getTimezoneOffset();
  const offsetDifference = offset - serverOffset;
  const unifiedTimestamp = new Date(timeString).getTime() - offsetDifference * 60 * 1000; // add miliseconds offset
  return moment(unifiedTimestamp).format('MM/DD/YYYY hh:mm:ss a');
};
