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
      <span>
        <b>{{ labels.PODS }} --</b>
      </span>
      <ol id="pods-list">
        <li v-bind:key="pod.name" v-for="pod in podsList">
          <b>{{ labels.NAME }}:</b> <i>{{ pod.name }}</i> <br/>
          <b>{{ labels.POD_CONDITIONS }}:</b> <i>{{ parseValue('state', pod.state) }}</i> <br/>
          <b>{{ labels.CONTAINERS }}:</b>
          <ul id="containers-list">
            <li v-bind:key="container.name" v-for="container in pod.containers">
              <b>{{ labels.NAME }}:</b> <i>{{ container.name }}</i> <br/>
              <b>{{ labels.RESOURCES }}: {{ labels.REQUESTS }}:</b> cpu - <i>{{ parseValue('resources', 'cpu', 'requests', container.resources) }}, </i>,
                                        memory - <i>{{ parseValue('resources', 'memory', 'requests', container.resources) }}</i> <br/>
              <b>{{ labels.RESOURCES }}: {{ labels.LIMITS }}:</b> cpu - <i>{{ parseValue('resources', 'cpu', 'limits', container.resources) }}, </i>,
              memory - <i>{{ parseValue('resources', 'memory', 'limits', container.resources) }}</i> <br/>
              <b>{{ labels.STATUS }}:</b> <i>{{ container.status }}</i>
            </li>
          </ul>
        </li>
      </ol>
    </v-flex>
  </v-layout>
</template>

<script>
import ELEMENTS_LABELS from '../../utils/constants/labels';

export default {
  name: 'ExpResourcesDetail',
  data () {
    return {
      labels: ELEMENTS_LABELS
    }
  },
  props: ['keyname', 'podsList'],
  methods: {
    parseValue: function (key, arg1, arg2, arg3) {
      switch (key) {
        case 'state':
          return Array.isArray(arg1) ? arg1.join(', ') : '--';
        case 'resources':
          if (!arg3) {
            return '--';
          }
          const resourceKind = arg2;
          const resourceType = arg1;
          return arg3[resourceKind][resourceType] ? arg3[resourceKind][resourceType] : '--';
        default:
          return arg1;
      }
    }
  }
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
</style>
