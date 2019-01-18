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
  <v-layout row wrap>
    <v-flex xs12 align-center>
      <h1>{{ messages.ERROR.INVALID_TOKEN.toUpperCase() }}</h1>
    </v-flex>
    <v-flex xs12>
      <h3>{{ messages.INFO.CONTACT_IT }}</h3>
    </v-flex>
  </v-layout>
</template>

<script>
import ELEMENT_LABELS from '../utils/constants/labels';
import MESSAGES from '../utils/constants/messages';

export default {
  name: 'InvalidToken',
  data () {
    return {
      labels: ELEMENT_LABELS,
      messages: MESSAGES
    }
  }
}
</script>

<style scoped>
h1 {
  font-family: 'Intel Clear Pro', sans-serif;
  font-size: 64px;
  margin-left: 100px;
  margin-top: 100px;
}
h3 {
  font-family: 'Intel Clear', sans-serif;
  margin-left: 100px;
}
</style>
