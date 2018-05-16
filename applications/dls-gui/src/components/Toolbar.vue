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
  <v-toolbar dark color="intel_primary" app fixed clipped-left height="110px">
    <v-toolbar-side-icon @click.stop="toggleMenu"></v-toolbar-side-icon>
    <v-toolbar-title>
      <v-container grid-list-md>
        <v-layout row >
          <v-flex md3>
            <img src="../img/intel-ai-acrnym-rgb-3000-wht.png"/>
          </v-flex>
          <v-flex md9 hidden-xs-only>
            DEEP LEARNING STUDIO
          </v-flex>
        </v-layout>
      </v-container>
    </v-toolbar-title>
    <v-spacer></v-spacer>
    <v-icon>ic_help_outline</v-icon>
    <v-btn flat>
      Andrzej
      <v-icon>keyboard_arrow_down</v-icon>
    </v-btn>
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

<style scoped>
.toolbar__title {
  overflow: visible;
  font-family: "Intel Clear Pro", sans-serif;
  font-size: 42px;
}
.toolbar__title img {
  margin-top: 14px;
}

</style>
