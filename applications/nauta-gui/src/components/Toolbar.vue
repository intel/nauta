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
  <v-toolbar dark color="intel_primary" app fixed clipped-left height="100px">
    <v-toolbar-side-icon v-if="menuBtnVisibility" @click.stop="toggleMenu"></v-toolbar-side-icon>
    <v-toolbar-title>
      <v-container grid-list-md>
        <v-layout row >
          <v-flex md6>
            <img src="../img/white_logo.png"/>
          </v-flex>
        </v-layout>
      </v-container>
    </v-toolbar-title>
    <v-spacer></v-spacer>
    <v-menu bottom offset-y>
      <v-btn flat slot="activator">
        <v-icon>import_contacts</v-icon>
      </v-btn>
      <v-list>
        <v-list-tile class="list__tile--link">
          <v-list-tile-title>
            <a href="/documentation/" target="_blank">
              {{ labels.USER_GUIDE }}
            </a>
          </v-list-tile-title>
        </v-list-tile>
        <v-list-tile class="list__tile--link">
          <v-list-tile-title>
            <a :href="licenseDoc" target="_blank" :download="labels.LICENSE_PDF">
              {{ labels.LICENSE }}
            </a>
          </v-list-tile-title>
        </v-list-tile>
      </v-list>
    </v-menu>
    <v-menu v-if="userboxParams.visible" bottom offset-y>
      <v-btn flat slot="activator">
        {{ username }}
        <v-icon>keyboard_arrow_down</v-icon>
      </v-btn>
      <v-list>
        <v-list-tile v-on:click="onSingOutBtnClick()">
          <v-list-tile-title>
            {{ labels.SIGN_OUT }}
          </v-list-tile-title>
        </v-list-tile>
      </v-list>
    </v-menu>
  </v-toolbar>
</template>

<script>
import {mapActions, mapGetters} from 'vuex';
import LicenseDoc from '../assets/license.pdf';
import ELEMENT_LABELS from '../utils/constants/labels';

export default {
  name: 'Toolbar',
  methods: {
    ...mapActions(['toggleMenu', 'handleLogOut']),
    onSingOutBtnClick: function () {
      this.handleLogOut('/signed_out');
    }
  },
  data () {
    return {
      labels: ELEMENT_LABELS,
      licenseDoc: LicenseDoc
    }
  },
  computed: {
    ...mapGetters({
      username: 'username',
      menuBtnVisibility: 'menuBtnVisibility',
      userboxParams: 'getUserboxParams'
    })
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
.list__tile__title {
  font-size: 14px;
}
a {
  text-decoration: none;
  color: inherit;
}

</style>
