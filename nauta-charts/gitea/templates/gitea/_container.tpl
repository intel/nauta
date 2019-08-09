{{/*
Create helm partial for gitea server
*/}}
{{- define "gitea" }}
- name: gitea
  image: {{ required "NAUTA Registry is required" .Values.global.nauta_registry }}/{{ .Values.images.gitea }}
  imagePullPolicy: {{ .Values.images.pullPolicy }}
  env:
  - name: POSTGRES_PASSWORD
    valueFrom:
      secretKeyRef:
        name: {{ template "db.fullname" . }}
        key: dbPassword
  {{- if .Values.admin_user.create }}
  - name: ADMIN_USERNAME
    valueFrom:
      secretKeyRef:
        name: {{ template "fullname" . }}-admin-secret
        key: name
  - name: ADMIN_PASSWORD
    valueFrom:
      secretKeyRef:
        name: {{ template "fullname" . }}-admin-secret
        key: password
  - name: ADMIN_EMAIL
    valueFrom:
      secretKeyRef:
        name: {{ template "fullname" . }}-admin-secret
        key: email
  lifecycle:
    postStart:
      exec:
        command:
          - '/bin/bash'
          - '-c'
          - >
            set +e;
            initial_wait=20;
            retries=10;
            interval=3;
            sleep ${initial_wait};
            for i in {1..$retries}; do
              admin_creation_result=$(su - git -c "/usr/local/bin/gitea admin create-user --name ${ADMIN_USERNAME} --password ${ADMIN_PASSWORD} --email ${ADMIN_EMAIL} --admin --config /data/gitea/conf/app.ini");
              if [[ $? -ne 0 ]] && [[ "${admin_creation_result}" != *"exists"* ]]; then
                sleep ${interval};
              else
                exit 0;
              fi
            done;
            exit 1;
  {{- end }}
  ports:
  - name: ssh
    containerPort: {{ .Values.service.ssh.port  }}
  - name: http
    containerPort: {{ .Values.service.http.port  }}
  livenessProbe:
    tcpSocket:
      port: http
    initialDelaySeconds: 200
    timeoutSeconds: 1
    periodSeconds: 10
    successThreshold: 1
    failureThreshold: 10
  readinessProbe:
    tcpSocket:
      port: http
    initialDelaySeconds: 5
    periodSeconds: 10
    successThreshold: 1
    failureThreshold: 3
  resources:
{{ toYaml .Values.resources.gitea | indent 10 }}
  volumeMounts:
  - name: gitea-data
    mountPath: /data
  - name: gitea-config
    mountPath: /etc/gitea
{{- end }}
