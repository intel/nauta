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
  <div id="app">
    <v-app>
      <div id="app-bg" :class="{intelBlue: !isLogged, intelGray: isLogged}">
        <Navigation v-if="isLogged"></Navigation>
        <Toolbar></Toolbar>
        <v-content>
          <v-container fluid>
            <router-view></router-view>
            <notifications group="app" width="400px" position="top right" class="pa-2">
              <template slot="body" slot-scope="props">
                <v-layout row>
                  <v-flex xs12>
                    <v-alert :value="true" :type="props.item.type" dismissible v-on:click="props.close">
                      {{ props.item.text }}
                    </v-alert>
                  </v-flex>
                </v-layout>
              </template>
            </notifications>
          </v-container>
        </v-content>
        <Footer v-if="isLogged"></Footer>
      </div>
    </v-app>
  </div>
</template>

<script>
import {mapGetters} from 'vuex';
import Navigation from './components/Navigation.vue';
import Toolbar from './components/Toolbar.vue';
import Footer from './components/Footer.vue';

export default {
  name: 'App',
  components: {
    Navigation,
    Toolbar,
    Footer
  },
  computed: {
    ...mapGetters({
      isLogged: 'isLogged',
      errorType: 'errorType',
      errorContent: 'errorContent'
    }),
    combinedError: function () {
      return {type: this.errorType, content: this.errorContent};
    }
  },
  watch: {
    combinedError: function (val) {
      this.$notify({group: 'app', text: val.content, type: val.type});
    }
  }
}
</script>

<style>
#app {
  font-family: 'Intel Clear', sans-serif;
  -webkit-font-smoothing: antialiased;
  -moz-osx-font-smoothing: grayscale;
  color: #ffffff;
  background-color: #f3f3f3;
}
#app-bg {
  height: 100%
}
.intelBlue {
  background-color: #003c71;
}
.intelGray {
  background-color: #f3f3f3;
}
</style>
