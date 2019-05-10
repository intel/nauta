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
  <v-footer app color="intel_lightest_gray">
    <v-layout row justify-center>
      &#9400; Intel Corporation. {{ labels.ALL_RIGHTS_RESERVED }}
      <a href="/documentation/TaC.html" target="_blank">{{ labels.TERMS_OF_USE }}</a>
    </v-layout>
  </v-footer>
</template>

<script>
import ELEMENT_LABELS from '../utils/constants/labels';

export default {
  name: 'FooterElement',
  data () {
    return {
      labels: ELEMENT_LABELS
    }
  }
}
</script>

<style scoped>
a {
  padding-left: 20px;
  text-decoration: none;
  color: inherit;
}
</style>
