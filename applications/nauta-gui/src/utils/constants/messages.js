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

import {toLocaleFormat} from '../../utils/timedate-utils'

export default {
  SUCCESS: {
    LAST_UPDATED_ON: (time) => `Last updated on ${toLocaleFormat(time)}`,
    NO_DATA: 'No data to display',
    NO_DATA_FOR_FILTER: 'No data for current search. Click on the RESET button and clear currently applied filters.',
    NO_DATA_FOR_CURRENT_USER: 'No data for currently signed user.',
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
    RETRY_SIGN_IN: 'To sign in, please return to the CLI and run the "nctl launch webui" command.'
  }
}
