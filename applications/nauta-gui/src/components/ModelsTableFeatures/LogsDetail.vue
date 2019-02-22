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
  <v-layout>
    <v-flex xs3>
      <span class="keyname">{{ keyname }}:</span>
    </v-flex>
    <v-flex xs9 class="values">
      <div class="row">
        <span class="kind">
          {{ `${labels.LOGS}, ${labels.ALL}` }}
        </span>
        <span class="links">
          <a :href="`/api/experiments/${name}/${owner}/logs/download`" :download="`${name}.txt`">{{ labels.DOWNLOAD }}</a>
        </span>
      </div>
      <div class="row">
        <span class="kind">
          {{ `${labels.LOGS}, ${labels.LAST} 100` }}
        </span>
        <span class="links">
          <a :href="`/api/experiments/${name}/${owner}/logs/last/show/100`" target="_blank">{{ labels.VIEW }}</a>
        </span>
      </div>
    </v-flex>
  </v-layout>
</template>

<script>
import ELEMENTS_LABELS from '../../utils/constants/labels';

export default {
  name: 'LogsDetail',
  data () {
    return {
      labels: ELEMENTS_LABELS
    }
  },
  props: ['keyname', 'name', 'owner']
}
</script>

<style scoped>
#pods-list {
  margin-left: 25px;
  font-size: 12px;
}
#containers-list {
  margin-left: 25px;
}
.keyname {
  font-weight: bold;
  font-size: 12px;
}
.values {
  margin-left: 20px;
  font-size: 12px;
}
.kind {
  margin-right: 30px;
  width: 100px;
  float: left;
}
</style>
