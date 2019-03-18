{{/*
Create helm partial for memcached
*/}}
{{- define "memcached" }}
- name: memcached
  image: {{ required "NAUTA Registry is required" .Values.global.nauta_registry }}/{{ .Values.images.memcached }}
  imagePullPolicy: {{ .Values.images.pullPolicy }}
  command:
    - memcached
    - -m {{ .Values.memcached.maxItemMemory  }}
    {{- if .Values.memcached.extendedOptions }}
    - -o
    - {{ .Values.memcached.extendedOptions }}
    {{- end }}
    {{- if .Values.memcached.verbosity }}
    - -{{ .Values.memcached.verbosity }}
    {{- end }}
  ports:
  - name: memcache
    containerPort: 11211
  livenessProbe:
    tcpSocket:
      port: memcache
    initialDelaySeconds: 30
    timeoutSeconds: 5
  readinessProbe:
    tcpSocket:
      port: memcache
    initialDelaySeconds: 5
    timeoutSeconds: 1
  resources:
{{ toYaml .Values.resources.memcached | indent 10 }}
{{- end }}
