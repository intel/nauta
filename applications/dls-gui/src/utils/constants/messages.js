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

export default {
  SUCCESS: {
    LAST_UPDATED_A_MOMENT_AGO: 'Last updated a moment ago',
    LAST_UPDATED_30S_AGO: 'Last updated over 30 seconds ago',
    NO_DATA: 'No data to display',
    NO_DATA_FOR_FILTER: 'No data for currently applied filters',
    SIGNED_OUT: 'You are signed out'
  },
  ERROR: {
    INTERNAL_SERVER_ERROR: 'Internal server error. Contact with administrator',
    INVALID_TOKEN: 'We\'re sorry, your token is invalid',
    UNEXPECTED_ERROR: 'We\'re sorry, unexpected error occured'
  },
  WARNING: {
    TB_INVALID_RUNS: 'Some of requested experiments cannot be visible in Tensorboard due to no output data provided.',
    TB_NOT_CREATED: 'Cannot create Tensorboard instance for requested experiments.'
  },
  INFO: {
    CONTACT_IT: 'Please contact your IT Administrator.',
    RETRY_SIGN_IN: 'To sign in, please return to the CLI and run the "dlsctl launch webui" command.'
  }
}
