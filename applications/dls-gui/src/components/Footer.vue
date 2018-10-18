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
  <v-footer app color="intel_lightest_gray">
    <v-layout row justify-center>
      &#9400; Intel Corporation. {{ labels.ALL_RIGHTS_RESERVED }}
      <a href="/documentation/Content/DLS4E%20V1.0/legal_disclaimer.htm" target="_blank">{{ labels.TERMS_OF_USE }}</a>
    </v-layout>
  </v-footer>
</template>

<script>
import ELEMENT_LABELS from '../utils/constants/labels';

export default {
  name: 'Footer',
  data () {
    return {
      labels: ELEMENT_LABELS
    }
  }
}
</script>

<style scoped>
a {
  padding-left: 20px;
  text-decoration: none;
  color: inherit;
}
</style>
