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
  <v-container grid-list-md>
    <v-layout row wrap text-xs-center>
      <v-flex xs4>
        <v-card color="red darken-1">
          <v-card-title class="title" primary-title>Current Experiments</v-card-title>
          <v-card-text class="headline">12</v-card-text>
        </v-card>
      </v-flex>
      <v-flex xs4>
        <v-card color="red darken-1">
          <v-card-title class="title" primary-title>Active Users</v-card-title>
          <v-card-text class="headline">1</v-card-text>
        </v-card>
      </v-flex>
      <v-flex xs4>
        <v-card color="red darken-1">
          <v-card-title class="title" primary-title>Workers Count</v-card-title>
          <v-card-text class="headline">4</v-card-text>
        </v-card>
      </v-flex>
      <v-flex xs12>
        <chart class="chart" :data="chart" :height="100"></chart>
      </v-flex>
    </v-layout>
    <v-layout row>
      <v-flex xs12>
        <v-card>
          <v-card-title>
            Experiments
            <v-spacer></v-spacer>
            <v-text-field append-icon="search" label="Search" single-line hide-details></v-text-field>
          </v-card-title>
          <v-data-table :headers="tableParams.columns" :items="tableParams.data" class="elevation-3">
            <template slot="items" slot-scope="props">
              <td>{{ props.item.id }}</td>
              <td>{{ props.item.modelName }}</td>
              <td>{{ props.item.trainingStatus }}</td>
              <td>{{ props.item.modelAccuracy }}</td>
              <td>{{ props.item.trainingSubmissionDate }}</td>
              <td>{{ props.item.trainingStartDate }}</td>
              <td>{{ props.item.trainingDuration }}</td>
              <td>{{ props.item.owner }}</td>
            </template>
          </v-data-table>
        </v-card>
      </v-flex>
    </v-layout>
  </v-container>
</template>

<script>
import {mapGetters, mapActions} from 'vuex';
import TestChart from './charts/lineChart';

export default {
  name: 'Dashboard',
  components: {
    chart: TestChart
  },
  data () {
    return {
      title: 'Dashboard',
      chart: {
        labels: ['January', 'February', 'March', 'April', 'May', 'June', 'July'],
        datasets: [
          {
            label: 'Experiments Count',
            backgroundColor: 'rgba(255,171,91,0.3)',
            data: [40, 20, 41, 16, 11, 23, 67]
          },
          {
            label: 'Results Count',
            backgroundColor: 'rgba(54,110,122,0.3)',
            data: [21, 1, 56, 13, 19, 22, 40]
          }
        ]
      },
      tableParams: {
        search: '',
        columns: [
          {text: 'ID', value: 'id'},
          {text: 'Model Name', value: 'modelName'},
          {text: 'Training Status', value: 'trainingStatus'},
          {text: 'Model Accuracy', value: 'modelAccuracy'},
          {text: 'Training Submission Date', value: 'trainingSubmissionDate'},
          {text: 'Training Start Date', value: 'trainingStartDate'},
          {text: 'Training Duration', value: 'trainingDuration'},
          {text: 'Owner', value: 'owner'}
        ],
        data: [
          {id: 1, modelName: 'exp1', trainingStatus: 'Running', modelAccuracy: '.61', trainingSubmissionDate: '4/10/2018, 9:10 am', trainingStartDate: '4/12/2018, 9:13 am', trainingDuration: '---', owner: 'ajoskows'},
          {id: 2, modelName: 'exp2', trainingStatus: 'Completed', modelAccuracy: '.91', trainingSubmissionDate: '2/1/2018, 2:30 pm', trainingStartDate: '2/1/2018, 2:31 pm', trainingDuration: '2 days, 16 hrs, 2 mins', owner: 'mariusz'}
        ]
      }
    }
  },
  methods: {
    ...mapActions([])
  },
  computed: {
    ...mapGetters({})
  }
}
</script>

<style scoped>
.chart {
  background-color: rgba(255, 255, 255, 0.9);
}
</style>
