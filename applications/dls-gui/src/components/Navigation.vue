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
  <v-navigation-drawer app clipped fixed v-model="visible">
    <v-list dense>
      <v-list-tile @click="test">
        <v-list-tile-action>
          <v-icon>dashboard</v-icon>
        </v-list-tile-action>
        <v-list-tile-content>
          <v-list-tile-title>Dashboard</v-list-tile-title>
        </v-list-tile-content>
      </v-list-tile>
      <v-list-tile @click="test">
        <v-list-tile-action>
          <v-icon>perm_media</v-icon>
        </v-list-tile-action>
        <v-list-tile-content>
          <v-list-tile-title>Models</v-list-tile-title>
        </v-list-tile-content>
      </v-list-tile>
      <v-list-tile @click="test">
        <v-list-tile-action>
          <v-icon>assessment</v-icon>
        </v-list-tile-action>
        <v-list-tile-content>
          <v-list-tile-title>Logs</v-list-tile-title>
        </v-list-tile-content>
      </v-list-tile>
      <v-list-tile @click="test">
        <v-list-tile-action>
          <v-icon>clear_all</v-icon>
        </v-list-tile-action>
        <v-list-tile-content>
          <v-list-tile-title>Example 1</v-list-tile-title>
        </v-list-tile-content>
      </v-list-tile>
      <v-list-tile @click="test">
        <v-list-tile-action>
          <v-icon>mail_outline</v-icon>
        </v-list-tile-action>
        <v-list-tile-content>
          <v-list-tile-title>Example 2</v-list-tile-title>
        </v-list-tile-content>
      </v-list-tile>
      <v-list-tile @click="test">
        <v-list-tile-action>
          <v-icon>multiline_chart</v-icon>
        </v-list-tile-action>
        <v-list-tile-content>
          <v-list-tile-title>Example 3</v-list-tile-title>
        </v-list-tile-content>
      </v-list-tile>
      <v-list-tile @click="test">
        <v-list-tile-action>
          <v-icon>settings</v-icon>
        </v-list-tile-action>
        <v-list-tile-content>
          <v-list-tile-title>Example 4</v-list-tile-title>
        </v-list-tile-content>
      </v-list-tile>
    </v-list>
  </v-navigation-drawer>
</template>

<script>
export default {
  name: 'Navigation',
  computed: {
    visible: {
      get () {
        return this.$store.state.app.menu.visible;
      },
      set () {}
    }
  },
  methods: {
    test: () => {
      console.log('test');
    }
  }
}
</script>

<style>

</style>
