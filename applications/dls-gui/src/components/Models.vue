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
  <v-layout row wrap>
    <ModelsTable :headers="tableParams.columns" :tableData="tableParams.data" :filterIcon="tableParams.filterIcon" :lastUpdate="dataTime"></ModelsTable>
  </v-layout>
</template>

<script>
import {mapGetters, mapActions} from 'vuex';
import ModelsTable from './ModelsTable'

export default {
  name: 'Models',
  components: {
    ModelsTable
  },
  data () {
    return {
      tableParams: {
        filterIcon: 'filter_list',
        search: '',
        columns: [
          {text: 'Model Name', value: 'modelName', sortable: true, filterable: true},
          {text: 'Training Status', value: 'trainingStatus', sortable: true, filterable: true},
          {text: 'Percent Complete', value: 'percentComplete', sortable: true},
          {text: 'Training Accuracy', value: 'trainingAccuracy', sortable: true},
          {text: 'Validation Accuracy', value: 'validationAccuracy', sortable: true},
          {text: 'Training Loss', value: 'trainingLoss', sortable: true},
          {text: 'Validation Loss', value: 'validationLoss', sortable: true},
          {text: 'Hyperparameter', value: 'hyperparameter', sortable: true},
          {text: 'Training Submission Date', value: 'trainingSubmissionDate', sortable: true},
          {text: 'Owner', value: 'owner', sortable: true, filterable: true}
        ],
        data: [
          {modelName: 'exp9', trainingStatus: 'Running', percentComplete: '.61', trainingAccuracy: '.61', validationAccuracy: '.63', trainingLoss: '.01', validationLoss: '.02', hyperparameter: '---', trainingSubmissionDate: '4/10/2018, 9:10 am', owner: 'ajoskows'},
          {modelName: 'exp2', trainingStatus: 'Failed', percentComplete: '.11', trainingAccuracy: '.21', validationAccuracy: '.93', trainingLoss: '.02', validationLoss: '.05', hyperparameter: '---', trainingSubmissionDate: '2/11/2018, 11:10 pm', owner: 'jchrapko'},
          {modelName: 'exp3', trainingStatus: 'Running', percentComplete: '.01', trainingAccuracy: '.11', validationAccuracy: '.13', trainingLoss: '.01', validationLoss: '.01', hyperparameter: '---', trainingSubmissionDate: '4/11/2018, 3:19 am', owner: 'dszyfelb'},
          {modelName: 'exp4', trainingStatus: 'Running', percentComplete: '.61', trainingAccuracy: '.61', validationAccuracy: '.63', trainingLoss: '.01', validationLoss: '.02', hyperparameter: '---', trainingSubmissionDate: '4/10/2018, 9:10 am', owner: 'ajoskows'},
          {modelName: 'exp5', trainingStatus: 'Running', percentComplete: '.11', trainingAccuracy: '.21', validationAccuracy: '.93', trainingLoss: '.02', validationLoss: '.05', hyperparameter: '---', trainingSubmissionDate: '2/11/2018, 11:10 pm', owner: 'jchrapko'},
          {modelName: 'exp6', trainingStatus: 'Running', percentComplete: '.01', trainingAccuracy: '.11', validationAccuracy: '.13', trainingLoss: '.01', validationLoss: '.01', hyperparameter: '---', trainingSubmissionDate: '4/11/2018, 3:19 am', owner: 'dszyfelb'}
        ]
      }
    }
  },
  methods: {
    ...mapActions([])
  },
  computed: {
    ...mapGetters({}),
    dataTime: function () {
      return Date.now() - 30 * 1000; // fake time 30s
    }
  }
}
</script>

<style scoped>

</style>
