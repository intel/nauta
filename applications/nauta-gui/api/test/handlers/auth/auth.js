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
const expect = require('chai').expect;
const sinon = require('sinon');
const rewire = require('rewire');
const Q = require('q');
const authApi = rewire('../../../src/handlers/auth/auth');
const errHandler = require('../../../src/utils/error-handler');
const errMessages = require('../../../src/utils/error-messages');
const HttpStatus = require('http-status-codes');

describe('Handlers | Auth', function () {

  let resMock, reqMock, deferred;

  const validToken = 'eyJhbGciOiJSUzI1NiIsImtpZCI6IiJ9.eyJpc3MiOiJrdWJlcm5ldGVzL3NlcnZpY2VhY2NvdW50Iiwia3Vi' +
    'ZXJuZXRlcy5pby9zZXJ2aWNlYWNjb3VudC9uYW1lc3BhY2UiOiJrdWJlLXN5c3RlbSIsImt1YmVybmV0ZXMuaW8vc2VydmljZWFjY291b' +
    'nQvc2VjcmV0Lm5hbWUiOiJuYXV0YS1rOHMtcGxhdGZvcm0tYWRtaW4tdG9rZW4tYzdyMjQiLCJrdWJlcm5ldGVzLmlvL3NlcnZpY2VhY2Nv' +
    'dW50L3NlcnZpY2UtYWNjb3VudC5uYW1lIjoibmF1dGEtazhzLXBsYXRmb3JtLWFkbWluIiwia3ViZXJuZXRlcy5pby9zZXJ2aWNlYWNjb3V' +
    'udC9zZXJ2aWNlLWFjY291bnQudWlkIjoiMDk4ZTZhY2MtOTJiYS0xMWU5LWFkNjEtNTI1ODE2MDYwMDAwIiwic3ViIjoic3lzdGVtOnNlcn' +
    'ZpY2VhY2NvdW50Omt1YmUtc3lzdGVtOm5hdXRhLWs4cy1wbGF0Zm9ybS1hZG1pbiJ9.M9IAoNIewWDuKn2b3F0pynPGIPdNU-s0eXA4u' +
    'GwRfoaucAuZqsQNxD66f41nyHxhlrUaAqJQXh0XMR3iBVpQRuutKvgJ_j6gQCFiPc2QWwDlI8qLc332_Z7VNezKpBh73iMIlkFhBPsHL' +
    'TvoFQgCj-gdtPyfy9XTSs99-4-evfrXyCmHHCw4wh-W7GF7Kb9wTg5sKOw8PgDzNVO-ThT7SUT0s86YWHAdSD4bhVbIGV2hIXpQH71oVU' +
    '9RfomW6-pmMRoOSP35LbhOhLpLTuIyb9SxHjpWEyDbRvZrDdFWXqc1y_69zNmc_sytYEfPLJWgq-qz7UOtRyNqIRQCh4Xylf9ydburJ' +
    'CqdW16z5pYsjd3RMRqkPbamhIYWKvpeAzBaZy9i2Q_jJn2lgNaJkjYt1NnRbX_EulkPCMRKp8gUSa-AI_o229_DVNG-QjI1evZfhIZB' +
    'Im2xKlhNlEwqhf37QGLdQsWUr3eEQo3-P6XjjPlD8_NGfD3G2mkpiQg3LfqvXnA3o19g2v0l50KeL3IvoyZp8UQOakyMWIH7GS4nlFH' +
    '4NehM1jXeXYOaitM1AneQ2uy46ScpzjEKNhWpisHU8noDYnl4tfqHVwFI7OdcFth575piB2ydmnlkuIk_AmWkHpK27fLM_hlqg48b0' +
    '6G_rDvxtYtehvVBHo7Zw-pteZ8';

  const fakeToken = 'fake_token';

  beforeEach(function () {
    resMock = {
      status: sinon.stub().returns({
        send: sinon.spy()
      }),
      send: sinon.spy()
    };
    reqMock = {
      body: {
        token: validToken
      }
    };
  });

  describe('parseJwtToken', function () {

    it('should return null if cannot decode token', function () {
      const expectedResult = null;
      const result = authApi.parseJwtToken(fakeToken);
      expect(result).to.equal(expectedResult);
    });

    it('should return payload if token correctly decoded', function () {
      const expectedResult = {
        'iss': 'kubernetes/serviceaccount',
        'kubernetes.io/serviceaccount/namespace': 'kube-system',
        'kubernetes.io/serviceaccount/secret.name': 'nauta-k8s-platform-admin-token-c7r24',
        'kubernetes.io/serviceaccount/service-account.name': 'nauta-k8s-platform-admin',
        'kubernetes.io/serviceaccount/service-account.uid': '098e6acc-92ba-11e9-ad61-525816060000',
        'sub': 'system:serviceaccount:kube-system:nauta-k8s-platform-admin'
      };
      const result = authApi.parseJwtToken(validToken);
      expect(result).to.deep.equal(expectedResult);
    });

  });

  describe('decodeToken', function () {
    let decoded;
    beforeEach(function () {
      decoded = {
        'kubernetes.io/serviceaccount/namespace': 'kube-system'
      };
    });

    it('should return error if cannot decode token', function () {
      return authApi.decodeToken(fakeToken)
        .catch(function (err) {
          expect(err.message).to.equal(errMessages.AUTH.INVALID_TOKEN);
        });
    });

    it('should return decoded data if token valid', function () {
      return authApi.decodeToken(validToken)
        .then(function (data) {
          expect(data['kubernetes.io/serviceaccount/namespace']).to.equal(decoded['kubernetes.io/serviceaccount/namespace'])
        });
    });
  });

  describe('getUserAuthority', function () {
    let decodeTokenMock, decoded;
    beforeEach(function () {
      decoded = {
        'kubernetes.io/serviceaccount/namespace': 'username'
      };
      deferred = Q.defer();
      decodeTokenMock = sinon.stub().returns(deferred.promise);
    });

    it('should return error if invalid request body', function () {
      delete reqMock.body.token;
      authApi.getUserAuthority(reqMock, resMock);
      expect(resMock.status.calledOnce).to.equal(true);
      expect(resMock.status.calledWith(400)).to.equal(true);
    });

    it('should return UNAUTHORIZED error if token is incorrect', function (done) {
      authApi.__set__('decodeToken', decodeTokenMock);
      authApi.getUserAuthority(reqMock, resMock);
      deferred.reject(errHandler(HttpStatus.UNAUTHORIZED, errMessages.AUTH.INVALID_TOKEN));
      process.nextTick(function () {
        expect(decodeTokenMock.calledOnce).to.equal(true);
        expect(resMock.status.calledOnce).to.equal(true);
        expect(resMock.status.calledWith(401)).to.equal(true);
        done();
      });
    });

    it('should return decoded token data if token is valid', function (done) {
      authApi.__set__('decodeToken', decodeTokenMock);
      authApi.getUserAuthority(reqMock, resMock);
      deferred.resolve(decoded);
      process.nextTick(function () {
        expect(resMock.send.calledOnce).to.equal(true);
        expect(resMock.send.getCall(0).args[0].decoded.username).to.equal(decoded['kubernetes.io/serviceaccount/namespace']);
        done();
      });
    });

  });
});
