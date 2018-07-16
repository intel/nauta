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

<template>
  <v-container fill-height justify-center>
    <v-progress-circular :size="90" indeterminate color="warning">Loading...</v-progress-circular>
  </v-container>
</template>

<script>
import {launchTensorBoard, checkIsTBInstanceReady} from '../store/handlers/tensorboard';
import RESPONSE_TYPES from '../utils/constants/message-types';
import RESPONSE_MESSAGES from '../utils/constants/messages';

const CHECK_TB_STATE_INTERVAL = 5000;

export default {
  name: 'TensorBoardCreator',
  data: () => {
    return {
      retry: 0,
      maxRetries: 20
    };
  },
  created: function () {
    const tensorboardParams = this.$route.query;
    let experimentsList = [];
    Object.keys(tensorboardParams).forEach((owner) => {
      if (Array.isArray(tensorboardParams[owner])) {
        tensorboardParams[owner].forEach((exp) => {
          experimentsList.push({
            name: exp,
            owner: owner
          });
        })
      } else {
        experimentsList.push({
          name: tensorboardParams[owner],
          owner: owner
        })
      }
    });
    const this2 = this;
    this.launch(experimentsList)
      .then((tb) => {
        const instanceUrl = tb.data.url;
        const instanceId = tb.data.id;
        this2.timerId = setInterval(() => {
          this2.check(instanceId)
            .then(() => {
              clearInterval(this2.timerId);
              window.location.assign(tb.data.url);
            })
            .catch(() => {
              this2.retry++;
              if (this2.retry > this2.maxRetries) {
                clearInterval(this2.timerId);
                this.$store.dispatch('showError', {type: RESPONSE_TYPES.ERROR, content: RESPONSE_MESSAGES.ERROR.INTERNAL_SERVER_ERROR});
              }
            });
        }, CHECK_TB_STATE_INTERVAL, instanceUrl, instanceId);
      })
      .catch(() => {
        this.$store.dispatch('showError', {type: RESPONSE_TYPES.ERROR, content: RESPONSE_MESSAGES.ERROR.INTERNAL_SERVER_ERROR});
      });
  },
  methods: {
    launch: function (expList) {
      return launchTensorBoard(expList);
    },
    check: function (id) {
      return checkIsTBInstanceReady(id);
    }
  }
}
</script>

<style scoped>

</style>
