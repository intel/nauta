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
  <div id="app">
    <v-app>
      <div id="app-bg"
           :class="{intelBlue: !isLogged, intelGray: isLogged}">
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
        <FooterElement v-if="isLogged"></FooterElement>
      </div>
    </v-app>
  </div>
</template>

<script>
import {mapGetters} from 'vuex';
import Navigation from './components/Navigation.vue';
import Toolbar from './components/Toolbar.vue';
import FooterElement from './components/Footer.vue';

export default {
  name: 'App',
  components: {
    Navigation,
    Toolbar,
    FooterElement
  },
  computed: {
    ...mapGetters({
      isLogged: 'isLogged',
      errorTime: 'errorTime',
      errorType: 'errorType',
      errorContent: 'errorContent'
    }),
    combinedError: function () {
      return {type: this.errorType, content: this.errorContent, time: this.errorTime};
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
.intelGrayTransparent {
  background-color: rgba(243, 243, 243, 0.12);
}
</style>
