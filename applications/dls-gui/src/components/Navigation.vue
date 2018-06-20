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
  <v-navigation-drawer v-if="!tensorMode" app clipped fixed v-model="visible">
    <v-list dense>
      <v-list-tile>
        <v-list-tile-action>
          <v-icon>track_changes</v-icon>
        </v-list-tile-action>
        <v-list-tile-content>
          <v-list-tile-title>Models</v-list-tile-title>
        </v-list-tile-content>
      </v-list-tile>
      <v-list-tile v-on:click="goToK8sDashboard()">
        <v-list-tile-action>
          <v-icon>dashboard</v-icon>
        </v-list-tile-action>
        <v-list-tile-content>
          <v-list-tile-title>Resources Dashboard</v-list-tile-title>
        </v-list-tile-content>
      </v-list-tile>
    </v-list>
  </v-navigation-drawer>
</template>

<script>
import {mapGetters} from 'vuex';
export default {
  name: 'Navigation',
  computed: {
    ...mapGetters({
      tensorMode: 'tensorMode'
    }),
    visible: {
      get () {
        return this.$store.state.app.menu.visible;
      },
      set (value) {
        this.$store.commit('setMenuVisibility', value);
      }
    }
  },
  methods: {
    goToK8sDashboard: () => {
      const hostname = window.location.origin;
      const k8sDashboardUrl = hostname + '/dashboard/';
      window.open(k8sDashboardUrl, '_blank');
    }
  }
}
</script>

<style scoped>
.navigation-drawer {
  background-color: #f3f3f3;
}
</style>
