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
  <v-toolbar app fixed clipped-left>
    <v-toolbar-side-icon @click.stop="toggleMenu"></v-toolbar-side-icon>
    <v-toolbar-title>
      <div class="logo">
        <img src="../img/logo.png" width="42">
      </div>
      Deep Learning Studio Enterprise
    </v-toolbar-title>
  </v-toolbar>
</template>

<script>
import {mapActions} from 'vuex';

export default {
  name: 'Toolbar',
  methods: {
    ...mapActions(['toggleMenu'])
  }
}
</script>

<style>
.logo {
  float: left;
  margin-right: 10px;
}
</style>
