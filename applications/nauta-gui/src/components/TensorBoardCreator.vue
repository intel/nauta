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
<template>
  <v-container fill-height justify-center>
    <v-progress-circular :size="90" indeterminate color="warning">
      {{ labels.LOADING }}...
    </v-progress-circular>
  </v-container>
</template>

<script>
import {launchTensorBoard, checkIsTBInstanceReady} from '../store/handlers/tensorboard';
import ELEMENT_LABELS from '../utils/constants/labels';
import RESPONSE_TYPES from '../utils/constants/message-types';
import RESPONSE_MESSAGES from '../utils/constants/messages';

const CHECK_TB_STATE_INTERVAL = 5000;

export default {
  name: 'TensorBoardCreator',
  data: () => {
    return {
      labels: ELEMENT_LABELS,
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
        const invalidRuns = tb.data.invalidRuns;
        if (!instanceUrl || !instanceId) {
          this.$store.dispatch('showError', {type: RESPONSE_TYPES.WARNING, content: RESPONSE_MESSAGES.WARNING.TB_NOT_CREATED});
          this.$router.push('/');
          return;
        }
        if (invalidRuns) {
          this.$store.dispatch('showError', {type: RESPONSE_TYPES.WARNING, content: RESPONSE_MESSAGES.WARNING.TB_INVALID_RUNS});
        }
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
