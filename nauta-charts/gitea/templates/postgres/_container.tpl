{{/*
Create helm partial for postgres server
*/}}
{{- define "postgres" }}
- name: postgres
  image: "{{ required "NAUTA Registry is required" .Values.global.nauta_registry }}/{{ .Values.images.postgres }}"
  imagePullPolicy: {{ default "" .Values.images.imagePullPolicy | quote }}
  args:
    {{- range $key, $value := default dict .Values.inPodPostgres.postgresConfig }}
    - -c
    - '{{ $key | snakecase }}={{ $value }}'
    {{- end }}
  env:
  - name: POSTGRES_USER
    value: {{ default "postgres" .Values.inPodPostgres.postgresUser | quote }}
  # Required for pg_isready in the health probes.
  - name: PGUSER
    value: {{ default "postgres" .Values.inPodPostgres.postgresUser | quote }}
  - name: POSTGRES_DB
    value: {{ default "" .Values.inPodPostgres.postgresDatabase | quote }}
  - name: POSTGRES_INITDB_ARGS
    value: {{ default "" .Values.inPodPostgres.postgresInitdbArgs | quote }}
  - name: PGDATA
    value: /var/lib/postgresql/data/pgdata
  - name: POSTGRES_PASSWORD
    valueFrom:
      secretKeyRef:
        name: {{ template "db.fullname" . }}
        key: dbPassword
  - name: POD_IP
    valueFrom: { fieldRef: { fieldPath: status.podIP } }
  ports:
  - name: postgresql
    containerPort: 5432
  livenessProbe:
    exec:
      command:
      - sh
      - -c
      - exec pg_isready --host $POD_IP
    initialDelaySeconds: 120
    timeoutSeconds: 5
    failureThreshold: 6
  readinessProbe:
    exec:
      command:
      - sh
      - -c
      - exec pg_isready --host $POD_IP
    initialDelaySeconds: 5
    timeoutSeconds: 3
    periodSeconds: 5
  resources:
{{ toYaml .Values.resources.postgres | indent 10 }}
  volumeMounts:
  - name: postgres-data
    mountPath: {{ .Values.inPodPostgres.dataMountPath }}
    subPath: {{ .Values.inPodPostgres.subPath }}
  {{- if .Values.usePasswordFile }}
  - name: password-file
    mountPath: /conf
    readOnly: true
  {{- end }}
{{- end }}
