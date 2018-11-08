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
