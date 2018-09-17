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
    <v-toolbar-side-icon v-if="menuBtnVisibility" @click.stop="toggleMenu"></v-toolbar-side-icon>
    <v-toolbar-title>
      <v-container grid-list-md>
        <v-layout row >
          <v-flex md3>
            <img src="../img/intel-ai-acrnym-rgb-3000-wht.png"/>
          </v-flex>
          <v-flex md9 hidden-xs-only>
            {{ labels.DLS.toUpperCase() }}
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
            <a :href="cliCommands" target="_blank" :download="labels.USER_GUIDE_PDF">
              {{ labels.USER_GUIDE }}
            </a>
          </v-list-tile-title>
        </v-list-tile>
        <v-list-tile class="list__tile--link">
          <v-list-tile-title>
            <a :href="releaseNotesDoc" target="_blank" :download="labels.RELEASE_NOTES_PDF">
              {{ labels.RELEASE_NOTES }}
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
import LicenseDoc from '../assets/dls-evaluation-license.pdf';
import ReleaseNotesDoc from '../assets/intel-release-notes-for-dell-early-access.pdf';
import CliCommands from '../assets/dls4e-cli-commands.pdf';
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
      licenseDoc: LicenseDoc,
      releaseNotesDoc: ReleaseNotesDoc,
      cliCommands: CliCommands
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
