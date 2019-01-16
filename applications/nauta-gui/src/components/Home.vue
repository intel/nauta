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
  <div>
    <v-container v-if="isLoadingAuth" fill-height justify-center>
      <v-progress-circular :size="90" indeterminate color="warning">
        {{ labels.LOADING }}...
      </v-progress-circular>
    </v-container>
    <v-layout row wrap v-if="!isLoadingAuth">
      <v-flex xs12 align-center>
        <h1>{{ messages.ERROR.UNEXPECTED_ERROR.toUpperCase() }}</h1>
      </v-flex>
      <v-flex xs12>
        <h3>{{ messages.INFO.CONTACT_IT }}</h3>
      </v-flex>
    </v-layout>
  </div>
</template>

<script>
import ELEMENT_LABELS from '../utils/constants/labels';
import MESSAGES from '../utils/constants/messages';
import {mapGetters, mapActions} from 'vuex';

export default {
  name: 'Home',
  data () {
    return {
      labels: ELEMENT_LABELS,
      messages: MESSAGES
    }
  },
  created: function () {
    const token = this.$route.query.token;
    this.$store.dispatch('loadAuthority', token)
      .then(() => {
        this.$router.push({path: '/models'});
      });
  },
  methods: {
    ...mapActions(['loadAuthority'])
  },
  computed: {
    ...mapGetters({
      isLoadingAuth: 'authLoadingState'
    })
  }
}
</script>

<style scoped>
h1 {
  font-family: 'Intel Clear Pro', sans-serif;
  font-size: 64px;
  margin-left: 100px;
  margin-top: 100px;
}
h3 {
  font-family: 'Intel Clear', sans-serif;
  margin-left: 100px;
}
</style>
