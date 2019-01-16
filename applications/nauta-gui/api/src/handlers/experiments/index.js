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
const express = require('express');
const expApi = require('./experiments');

const router = express.Router();

router.get('/list', expApi.getUserExperiments);
router.get('/:experiment/resources', expApi.getExperimentResourcesData);
router.get('/:experiment/:owner/logs/last/:mode/:number', expApi.getExperimentLogs);
router.get('/:experiment/:owner/logs/download', expApi.getAllExperimentLogs);

module.exports = router;
