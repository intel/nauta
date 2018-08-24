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

export default function (timedateA, timedateB) {
  const startTime = new Date(timedateA);
  const endTime = new Date(timedateB);
  let diff = (endTime.getTime() - startTime.getTime()) / 1000; // in seconds
  const days = Math.floor(diff / 60 / 60 / 24);
  diff -= days * 60 * 60 * 24;
  const hours = Math.floor(diff / 60 / 60);
  diff -= hours * 60 * 60;
  const minutes = Math.floor(diff / 60);
  diff -= minutes * 60;
  return {
    days,
    hours,
    minutes,
    seconds: diff
  };
}
