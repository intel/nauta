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
const config = require('./config');
const path = require('path');
const express = require('express');
const logger = require('./src/utils/logger');
const bodyParser = require('body-parser');
const HttpStatus = require('http-status-codes');

const app = express();

// configuration
app.use(bodyParser.urlencoded({ extended: false }));
app.use(bodyParser.json());
app.use(function (req, res, next) {
  res.header('Access-Control-Allow-Origin', '*');
  res.header('Access-Control-Allow-Headers', 'Origin, X-Requested-With, Content-Type, Accept');
  next();
});
app.use(express.static('dist'));

// handlers mappings
app.use('/api/auth', require('./src/handlers/auth'));
app.use('/api/experiments', require('./src/handlers/experiments'));
app.use('/api/tensorboard', require('./src/handlers/tensorboard'));

app.get('/*', function (req, res) {
  res.sendFile(path.join(__dirname, '../dist/index.html'), function (err) {
    if (err) {
      res.status(HttpStatus.INTERNAL_SERVER_ERROR).send(err);
    }
  });
});

// server start listening
app.listen(config.port, () => {
  logger.info('API listening on port %d...', config.port);
});
