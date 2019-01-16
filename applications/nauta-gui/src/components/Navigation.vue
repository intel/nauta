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
  <v-navigation-drawer app clipped fixed v-model="visible" ref="navelement">
    <v-list dense>
      <v-list-tile>
        <v-list-tile-action>
          <v-icon>track_changes</v-icon>
        </v-list-tile-action>
        <v-list-tile-content>
          <v-list-tile-title>{{ labels.EXPERIMENTS }}</v-list-tile-title>
        </v-list-tile-content>
      </v-list-tile>
      <v-list-tile v-on:click="goToK8sDashboard()">
        <v-list-tile-action>
          <v-icon>dashboard</v-icon>
        </v-list-tile-action>
        <v-list-tile-content>
          <v-list-tile-title>{{ labels.RESOURCES_DASHBOARD }}</v-list-tile-title>
        </v-list-tile-content>
      </v-list-tile>
    </v-list>
  </v-navigation-drawer>
</template>

<script>
import ELEMENT_LABELS from '../utils/constants/labels';
import {mapGetters, mapActions, mapMutations} from 'vuex';

export default {
  name: 'Navigation',
  data () {
    return {
      labels: ELEMENT_LABELS
    }
  },
  computed: {
    ...mapGetters({
      username: 'username',
      menuVisibility: 'menuVisibility'
    }),
    visible: {
      get () {
        return this.menuVisibility;
      },
      set (value) {
        this.setMenuVisibility(value);
      }
    }
  },
  methods: {
    ...mapActions(['logIntoK8SDashboard']),
    ...mapMutations(['setMenuVisibility']),
    goToK8sDashboard () {
      this.logIntoK8SDashboard()
        .then(() => {
          const hostname = window.location.origin;
          const k8sDashboardUrl = `${hostname}/dashboard/#!/overview?namespace=${this.username}`;
          window.open(k8sDashboardUrl, '_blank');
        });
    },
    documentClick (e) {
      const navElement = this.$refs.navelement.$vnode.elm;
      const targetElement = e.target;
      if (navElement !== targetElement) {
        this.setMenuVisibility(false);
      }
    }
  },
  created () {
    document.addEventListener('click', this.documentClick);
  },
  destroyed () {
    document.removeEventListener('click', this.documentClick);
  }
}
</script>

<style scoped>
.navigation-drawer {
  background-color: #f3f3f3;
}
</style>
